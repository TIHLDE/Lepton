from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import (
    BasePermissionModel,
    check_has_access,
    set_user_id,
)
from app.content.models import Category
from app.content.models.priority import Priority
from app.content.models.user import User
from app.forms.enums import EventFormType
from app.group.models.group import Group
from app.util.models import BaseModel, OptionalImage
from app.util.utils import now, yesterday


class Event(BaseModel, OptionalImage, BasePermissionModel):

    write_access = AdminGroup.admin()

    title = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200, null=True)
    description = models.TextField(default="", blank=True)
    category = models.ForeignKey(
        Category, blank=True, null=True, default=None, on_delete=models.SET_NULL
    )
    organizer = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="events",
    )

    """ Strike fields """
    can_cause_strikes = models.BooleanField(default=True)
    enforces_previous_strikes = models.BooleanField(default=True)

    """ Registration fields """
    sign_up = models.BooleanField(default=False)
    limit = models.IntegerField(default=0)
    closed = models.BooleanField(default=False)
    registered_users_list = models.ManyToManyField(
        User,
        through="Registration",
        through_fields=("event", "user"),
        blank=True,
        default=None,
        verbose_name="registered users",
    )
    start_registration_at = models.DateTimeField(blank=True, null=True, default=None)
    end_registration_at = models.DateTimeField(blank=True, null=True, default=None)
    sign_off_deadline = models.DateTimeField(blank=True, null=True, default=None)
    registration_priorities = models.ManyToManyField(
        Priority, blank=True, default=None, related_name="priorities"
    )
    only_allow_prioritized = models.BooleanField(default=False)

    """ Cronjob fields """
    runned_post_event_actions = models.BooleanField(default=False)
    runned_sign_off_deadline_reminder = models.BooleanField(default=False)

    class Meta:
        ordering = ("start_date",)

    def __str__(self):
        return f"{self.title} - starting {self.start_date} at {self.location}"

    @property
    def website_url(self):
        return f"/arrangementer/{self.id}/"

    @property
    def expired(self):
        return self.end_date <= yesterday()

    @property
    def list_count(self):
        """Number of users registered to attend the event"""
        return self.get_participants().count()

    @property
    def waiting_list_count(self):
        """Number of users on the waiting list"""
        return self.get_waiting_list().count()

    def get_has_attended(self):
        return self.get_participants().filter(has_attended=True)

    def get_participants(self):
        return self.registrations.filter(is_on_wait=False)

    def get_waiting_list(self):
        """Number of users on the waiting list"""
        return self.registrations.filter(is_on_wait=True)

    def user_has_attended_event(self, user):
        return self.get_participants().filter(user=user, has_attended=True).exists()

    @property
    def is_past_sign_off_deadline(self):
        return now() >= self.sign_off_deadline

    def is_two_hours_before_event_start(self):
        return now() >= self.start_date - timedelta(hours=2)

    @property
    def event_has_ended(self):
        return now() >= self.end_date

    def has_waiting_list(self):
        return self.has_limit() and (self.is_full or self.get_waiting_list().exists())

    def has_limit(self):
        return self.limit != 0

    @property
    def is_full(self):
        return self.has_limit() and self.get_participants().count() >= self.limit

    def has_priorities(self):
        return self.registration_priorities.all().exists()

    @property
    def evaluation(self):
        return self.forms.filter(type=EventFormType.EVALUATION).first()

    @property
    def survey(self):
        return self.forms.filter(type=EventFormType.SURVEY).first()

    def check_request_user_has_access_through_organizer(self, user, organizer):
        return user.memberships_with_events_access.filter(group=organizer).exists()

    def has_object_statistics_permission(self, request):
        return self.has_object_write_permission(request)

    def has_object_write_permission(self, request):
        if request.id is None:
            set_user_id(request)

        if request.user is None:
            return False

        has_access_to_new_organizer = (
            self.check_request_user_has_access_through_organizer(
                request.user, request.data["organizer"]
            )
            if request.data.get("organizer", None)
            and request.data["organizer"] != self.organizer
            else True
        )

        has_access_to_current_and_new_organizer = (
            (
                self.check_request_user_has_access_through_organizer(
                    request.user, self.organizer
                )
                and has_access_to_new_organizer
            )
            if self.organizer
            else request.user.memberships_with_events_access.exists()
        )

        return (
            check_has_access(self.write_access, request)
            or has_access_to_current_and_new_organizer
        )

    @classmethod
    def has_write_permission(cls, request):
        if request.user is None:
            return False
        return (
            (
                check_has_access(cls.write_access, request)
                or cls.check_request_user_has_access_through_organizer(
                    cls, request.user, request.data["organizer"]
                )
            )
            if request.data.get("organizer", None)
            else request.user.memberships_with_events_access.exists()
        )

    def clean(self):
        self.validate_start_end_registration_times()

    def validate_start_end_registration_times(self):
        self.check_sign_up_and_registration_times()
        self.check_if_registration_is_not_set()
        self.check_sign_up_and_sign_off_deadline()
        self.check_start_time_is_after_end_time()
        if self.sign_up:
            self.check_start_time_is_before_end_registration()
            self.check_start_registration_is_before_end_registration()
            self.check_start_registration_is_after_start_time()
            self.check_start_registration_is_after_deadline()
            self.check_end_time_is_before_end_registration()
            self.check_start_date_is_before_deadline()

    def check_sign_up_and_registration_times(self):
        if not self.sign_up and (
            self.start_registration_at or self.end_registration_at
        ):
            raise ValidationError(
                "Enable signup to set start_date and end time for registration."
            )

    def check_if_registration_is_not_set(self):
        if self.sign_up and not (
            self.start_registration_at
            and self.end_registration_at
            and self.sign_off_deadline
        ):
            raise ValidationError(
                "Set start- and end-registration and sign_off_deadline"
            )

    def check_sign_up_and_sign_off_deadline(self):
        if not self.sign_up and self.sign_off_deadline:
            raise ValidationError("Enable signup to add deadline.")

    def check_start_time_is_before_end_registration(self):
        if self.start_date < self.end_registration_at:
            raise ValidationError(
                "End time for registration cannot be after the event start_date."
            )

    def check_start_registration_is_before_end_registration(self):
        if self.start_registration_at > self.end_registration_at:
            raise ValidationError(
                "Start time for registration cannot be after end time."
            )

    def check_start_registration_is_after_start_time(self):
        if self.start_date < self.start_registration_at:
            raise ValidationError(
                "Event start_date time for registration cannot be after start_date time."
            )

    def check_end_time_is_before_end_registration(self):
        if self.end_date < self.end_registration_at:
            raise ValidationError(
                "End time for registration cannot be after the event end_date."
            )

    def check_start_date_is_before_deadline(self):
        if self.start_date < self.sign_off_deadline:
            raise ValidationError(
                "End time for sign_off cannot be after the event start_date."
            )

    def check_start_registration_is_after_deadline(self):
        if self.start_registration_at > self.sign_off_deadline:
            raise ValidationError(
                "End time for sign_off cannot be after the event start_registration_at."
            )

    def check_start_time_is_after_end_time(self):
        if self.end_date < self.start_date:
            raise ValidationError(
                "End date for event cannot be before the event start_date."
            )
