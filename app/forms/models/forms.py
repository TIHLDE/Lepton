import uuid

from django.db import models

from enumchoicefield import EnumChoiceField
from polymorphic.models import PolymorphicModel

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel, check_has_access
from app.content.models.event import Event
from app.content.models.user import User
from app.forms.enums import EventFormType, FormFieldType
from app.util.models import BaseModel


class Form(PolymorphicModel):
    write_access = [AdminGroup.HS, AdminGroup.NOK, AdminGroup.INDEX]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Form"
        verbose_name_plural = "Forms"

    def __str__(self):
        return self.title

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
    def has_list_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_write_permission(cls, request):
        if not request.user:
            return False
        return check_has_access(cls.write_access, request)

    def has_object_write_permission(self, request):
        if isinstance(self, EventForm) and self.type == EventFormType.EVALUATION:
            return (
                self.event.get_queue()
                .filter(user=request.user, has_attended=True)
                .exists()
            )
        return True

    def has_object_read_permission(self, request):
        if isinstance(self, EventForm) and self.type == EventFormType.EVALUATION:
            return (
                self.event.get_queue()
                .filter(user=request.user, has_attended=True)
                .exists()
            )
        return True


class EventForm(Form):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="forms")
    type = EnumChoiceField(EventFormType, default=EventFormType.SURVEY)

    class Meta:
        unique_together = ("event", "type")
        verbose_name = "Event form"
        verbose_name_plural = "Event forms"


class Field(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="fields")
    type = EnumChoiceField(FormFieldType, default=FormFieldType.TEXT_ANSWER)
    required = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def add_options(self, options):
        for option in options:
            Option.objects.create(field=self, **option)


class Option(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, default="")
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="options")

    def __str__(self):
        return self.title


class Submission(BaseModel, BasePermissionModel):
    read_access = AdminGroup.admin()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="submissions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")

    class Meta:
        unique_together = ("form", "user")

    def __str__(self):
        return f"{self.user.user_id}'s submission to {self.form}"

    @classmethod
    def has_write_permission(cls, request):
        return True

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
    answer_text = models.CharField(max_length=255, blank=True)

    def get_field(self):
        return self.field if self.field else self.selected_options.first().field

    def __str__(self):
        return f"Answer to {self.submission}"
