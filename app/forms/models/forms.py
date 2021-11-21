import uuid

from django.db import models, transaction

from enumchoicefield import EnumChoiceField
from ordered_model.models import OrderedModel
from polymorphic.models import PolymorphicModel

from app.common.enums import AdminGroup, Groups
from app.common.permissions import BasePermissionModel, check_has_access
from app.content.models.event import Event
from app.content.models.user import User
from app.forms.enums import EventFormType, FormFieldType
from app.group.models import Group
from app.util.models import BaseModel


class Form(PolymorphicModel, BasePermissionModel):
    write_access = [
        AdminGroup.HS,
        AdminGroup.NOK,
        AdminGroup.SOSIALEN,
        AdminGroup.INDEX,
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    template = models.BooleanField(default=False)

    # TODO: https://github.com/TIHLDE/Lepton/issues/286
    viewer_has_answered = None

    class Meta:
        verbose_name = "Form"
        verbose_name_plural = "Forms"

    def __str__(self):
        return self.title

    @property
    def website_url(self):
        return f"/sporreskjema/{self.id}/"

    def add_fields(self, fields):
        for field in fields:
            options = field.pop("options", None)
            field = Field.objects.create(form=self, **field)

            if options:
                field.add_options(options)

    @classmethod
    def has_retrieve_permission(cls, request):
        if not request.user:
            return False
        return True

    @classmethod
    def has_statistics_permission(cls, request):
        return True

    def has_object_statistics_permission(self, request):
        return check_has_access(self.write_access, request)

    @classmethod
    def has_list_permission(cls, request):
        if not request.user:
            return False
        if cls.is_group_form(request):
            return GroupForm.has_list_permission(request)
        return request.user.memberships_with_events_access.exists()

    @classmethod
    def is_group_form(cls, request):
        """
        DRY Rest Permissions cannot handle polymorphic models
        which requires a manual workaround for the type of form.
        """
        return request.data.get("resource_type") == "GroupForm"

    @classmethod
    def has_write_permission(cls, request):
        if not request.user:
            return False

        if cls.is_group_form(request):
            return GroupForm.has_write_permission(request)

        return bool(request.user)

    @classmethod
    def has_create_permission(cls, request):
        if not request.user:
            return False

        if request.data.get("resource_type", "") == "EventForm":
            event = Event.objects.get(id=request.data.get("event"))
            return event.has_object_write_permission(request)

        if cls.is_group_form(request):
            return GroupForm.has_write_permission(request)

        return check_has_access(cls.write_access, request)

    def has_object_write_permission(self, request):
        return check_has_access(self.write_access, request)

    def has_object_read_permission(self, request):
        if not request.user:
            return False
        return True


class EventForm(Form):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="forms")
    type = EnumChoiceField(EventFormType, default=EventFormType.SURVEY)

    class Meta:
        unique_together = ("event", "type")
        verbose_name = "Event form"
        verbose_name_plural = "Event forms"

    def has_event_permission(self, request):
        if request.user is None:
            return False

        return self.event.has_object_write_permission(request)

    def has_object_statistics_permission(self, request):
        return self.has_event_permission(request)

    def has_object_write_permission(self, request):
        return self.has_event_permission(request)

    def has_object_read_permission(self, request):
        if self.type == EventFormType.EVALUATION:
            return self.event.user_has_attended_event(
                request.user
            ) or self.has_event_permission(request)
        return True


class GroupForm(Form):

    read_access = [Groups.TIHLDE]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="forms")

    class Meta:
        verbose_name = "Group form"
        verbose_name_plural = "Group forms"

    @classmethod
    def has_write_permission(cls, request):
        group_slug = request.data.get("group")
        group = Group.objects.filter(slug=group_slug).first()

        return request.user.is_member_of(group) or check_has_access(
            cls.write_access, request
        )

    @classmethod
    def has_list_permission(cls, request):
        if not request.user:
            return False
        return check_has_access(cls.read_access, request)


class Field(OrderedModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="fields")
    type = EnumChoiceField(FormFieldType, default=FormFieldType.TEXT_ANSWER)
    required = models.BooleanField(default=False)
    order_with_respect_to = "form"

    def __str__(self):
        return self.title

    def add_options(self, options):
        for option in options:
            Option.objects.create(field=self, **option)

    class Meta(OrderedModel.Meta):
        pass


class Option(OrderedModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, default="")
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="options")
    order_with_respect_to = "field"

    def __str__(self):
        return self.title

    class Meta(OrderedModel.Meta):
        pass


class Submission(BaseModel, BasePermissionModel):
    read_access = [AdminGroup.HS, AdminGroup.INDEX, AdminGroup.SOSIALEN, AdminGroup.NOK]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="submissions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")

    class Meta:
        unique_together = ("form", "user")

    def __str__(self):
        return f"{self.user.user_id}'s submission to {self.form}"

    @transaction.atomic
    def save(self, *args, **kwargs):
        if isinstance(self.form, EventForm):
            user_has_registration = not self.form.event.registrations.filter(
                user=self.user
            ).exists()
            if user_has_registration:
                Submission.objects.filter(user=self.user, form=self.form).delete()
        super().save(*args, **kwargs)

    @classmethod
    def has_write_permission(cls, request):
        if request.user is None:
            return False
        if not request.user.is_authenticated:
            return False
        if request.parser_context["view"].action in ["create"]:
            return True
        return check_has_access(cls.read_access, request)

    @classmethod
    def has_retrieve_permission(cls, request):

        if request.user is None:
            return False

        return cls._is_own_permission(request) or check_has_access(
            cls.read_access, request
        )

    @classmethod
    def _is_own_permission(cls, request):
        form_id = request.parser_context["kwargs"]["form_id"]
        form = Form.objects.get(id=form_id)

        submission_id = request.parser_context["kwargs"]["pk"]
        submission = form.submissions.get(id=submission_id)

        return submission.user is request.user

    @classmethod
    def has_list_permission(cls, request):

        if request.user is None:
            return False

        return check_has_access(cls.read_access, request)

    def has_object_read_permission(self, request):
        return self._is_own_permission(request) or check_has_access(
            self.read_access, request
        )


class Answer(BaseModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="answers"
    )
    selected_options = models.ManyToManyField(
        Option, related_name="answers", blank=True
    )
    field = models.ForeignKey(
        Field, on_delete=models.CASCADE, related_name="answers", blank=True, null=True
    )
    answer_text = models.TextField(default="", blank=True)

    def get_field(self):
        return self.field if self.field else self.selected_options.first().field

    def __str__(self):
        return f"Answer to {self.submission}"
