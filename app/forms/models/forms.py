import uuid

from django.core.mail import send_mail
from django.db import models, transaction

from ordered_model.models import OrderedModel
from polymorphic.models import PolymorphicModel

from app.common.enums import AdminGroup, Groups
from app.common.permissions import BasePermissionModel, check_has_access
from app.content.models.event import Event
from app.content.models.user import User
from app.forms.enums import NativeEventFormType as EventFormType
from app.forms.enums import NativeFormFieldType as FormFieldType
from app.forms.exceptions import (
    DuplicateSubmission,
    FormNotOpenForSubmission,
    GroupFormOnlyForMembers,
)
from app.group.models import Group
from app.util.models import BaseModel


class Form(PolymorphicModel, BasePermissionModel):
    write_access = (*AdminGroup.admin(), AdminGroup.NOK)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=400)
    description = models.TextField(blank=True, default="")
    template = models.BooleanField(default=False)

    viewer_has_answered = None

    class Meta:
        ordering = ("title",)
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
    def is_event_form(cls, request):
        return request.data.get("resource_type") == "EventForm"

    @classmethod
    def is_group_form(cls, request):
        return request.data.get("resource_type") == "GroupForm"

    @classmethod
    def has_retrieve_permission(cls, request):
        if not request.user:
            return False
        return True

    @classmethod
    def has_statistics_permission(cls, _request):
        return True

    def has_object_statistics_permission(self, request):
        return check_has_access(self.write_access, request)

    @classmethod
    def has_list_permission(cls, request):
        if not request.user:
            return False
        if cls.is_group_form(request):
            return GroupForm.has_list_permission(request)
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_write_permission(cls, request):
        if not request.user:
            return False

        if cls.is_group_form(request):
            return GroupForm.has_write_permission(request)
        if cls.is_event_form(request):
            return EventForm.has_write_permission(request)

        return bool(request.user)

    @classmethod
    def has_create_permission(cls, request):
        if not request.user:
            return False

        if cls.is_event_form(request):
            return EventForm.has_create_permission(request)
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
    type = models.CharField(
        max_length=40, choices=EventFormType.choices, default=EventFormType.SURVEY
    )

    class Meta:
        unique_together = ("event", "type")
        verbose_name = "Event form"
        verbose_name_plural = "Event forms"

    @classmethod
    def has_write_permission(cls, request):
        event_id = request.data.get("event")
        event = Event.objects.filter(id=event_id).first()

        return (
            event
            and event.has_object_write_permission(request)
            or request.user.memberships_with_events_access.exists()
        )

    @classmethod
    def has_create_permission(cls, request):
        event = Event.objects.get(id=request.data.get("event"))
        return event.has_object_write_permission(request)

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
    email_receiver_on_submit = models.EmailField(max_length=200, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="forms")
    can_submit_multiple = models.BooleanField(default=True)
    is_open_for_submissions = models.BooleanField(default=False)
    only_for_group_members = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Group form"
        verbose_name_plural = "Group forms"

    @classmethod
    def has_write_permission(cls, request):
        if request.method == "POST":
            group_slug = request.data.get("group")
            group = Group.objects.filter(slug=group_slug).first()
        else:
            form_id = request.parser_context.get("kwargs", {}).get("pk", None)
            form = GroupForm.objects.filter(id=form_id).first()
            group = form.group if form else None
        return (
            (group and group.has_object_group_form_permission(request))
            or check_has_access(cls.write_access, request)
            or request.user.is_leader
        )

    @classmethod
    def has_list_permission(cls, request):
        if not request.user:
            return False
        return check_has_access(cls.read_access, request)

    def has_object_statistics_permission(self, request):
        return self.has_object_write_permission(request)

    def has_object_read_permission(self, request):
        if self.has_object_write_permission(request):
            return True
        if not self.is_open_for_submissions:
            return False
        if self.only_for_group_members:
            return request.user.is_member_of(self.group)
        return True

    def has_object_write_permission(self, request):
        return self.group.has_object_group_form_permission(request) or check_has_access(
            self.write_access, request
        )


class Field(OrderedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=400)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="fields")
    type = models.CharField(
        max_length=40, choices=FormFieldType.choices, default=FormFieldType.TEXT_ANSWER
    )
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
    title = models.CharField(max_length=400, default="")
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="options")
    order_with_respect_to = "field"

    def __str__(self):
        return self.title

    class Meta(OrderedModel.Meta):
        pass


class Submission(BaseModel, BasePermissionModel):
    read_access = AdminGroup.admin()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="submissions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")

    def __str__(self):
        return f"{self.user.user_id}'s submission to {self.form}"

    def send_group_form_submission_email(self):
        from app.communication.notifier import send_html_email
        from app.util.mail_creator import MailCreator

        send_html_email(
            [self.form.email_receiver_on_submit],
            MailCreator(f'Noen har svart på "{self.form.title}"')
            .add_paragraph(
                f'{self.user.first_name} {self.user.last_name} har besvart spørreskjemaet "{self.form.title}"'
            )
            .add_button(
                "Se spørreskjema",
                self.form.group.website_url,
            )
            .generate_string(),
            "Nytt spørreskjema svar",
        )

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.full_clean()
        if isinstance(self.form, GroupForm) and self.form.email_receiver_on_submit:
            self.send_group_form_submission_email()
        super().save(*args, **kwargs)

    def clean(self):
        self.check_multiple_submissions()
        if isinstance(self.form, GroupForm):
            self.check_group_form_open_for_submissions()
            self.check_group_form_only_for_members()

    def check_multiple_submissions(self):
        existing_same_user_and_form = Submission.objects.filter(
            user=self.user, form=self.form
        )
        if existing_same_user_and_form.exists():
            if isinstance(self.form, EventForm):
                self.check_event_form_has_registration()
                Submission.objects.filter(user=self.user, form=self.form).delete()
            elif isinstance(self.form, GroupForm):
                self.check_group_form_can_submit_multiple()
            else:
                raise DuplicateSubmission()

    def check_event_form_has_registration(self):
        user_has_registration = self.form.event.registrations.filter(
            user=self.user
        ).exists()
        if user_has_registration:
            raise DuplicateSubmission(
                "Du kan ikke endre innsendt spørreskjema etter påmelding"
            )

    def check_group_form_can_submit_multiple(self):
        if not self.form.can_submit_multiple:
            raise DuplicateSubmission()

    def check_group_form_open_for_submissions(self):
        if not self.form.is_open_for_submissions:
            raise FormNotOpenForSubmission()

    def check_group_form_only_for_members(self):
        if self.form.only_for_group_members and not self.user.is_member_of(
            self.form.group
        ):
            raise GroupFormOnlyForMembers()

    @classmethod
    def _get_form_from_request(cls, request):
        form_id = request.parser_context.get("kwargs", {}).get("form_id", None)
        if form_id:
            return Form.objects.get(id=form_id)

        return None

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

        form = cls._get_form_from_request(request)

        if not form:
            return False

        return cls._is_own_permission(request) or form.has_object_write_permission(
            request
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
        form = cls._get_form_from_request(request)
        return form.has_object_write_permission(request)

    def has_object_read_permission(self, request):
        return self._is_own_permission(request) or check_has_access(
            self.read_access, request
        )

    @classmethod
    def has_download_permission(cls, request):
        return cls.has_list_permission(request)


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
