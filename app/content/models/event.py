from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import signals
from django.utils.translation import gettext as _

from app.util.models import BaseModel, OptionalImage
from app.util.utils import today, yesterday

from ..signals import send_event_reminders
from .category import Category
from .prioritiy import Priority
from .registration import Registration
from .user import User


class Event(BaseModel, OptionalImage):
    title = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200, null=True)
    description = models.TextField(default="", blank=True)
    PRIORITIES = (
        (0, "Low"),
        (1, "Normal"),
        (2, "High"),
    )
    priority = models.IntegerField(default=0, choices=PRIORITIES, null=True)
    category = models.ForeignKey(
        Category, blank=True, null=True, default=None, on_delete=models.SET_NULL
    )

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
    evaluate_link = models.CharField(max_length=200, blank=True, null=True)
    end_date_schedular_id = models.CharField(max_length=100, blank=True, null=True)
    sign_off_deadline_schedular_id = models.CharField(
        max_length=100, blank=True, null=True
    )

    def __str__(self):
        return f"{self.title} - starting {self.start_date} at {self.location}"

    @property
    def expired(self):
        return self.end_date <= yesterday()

    @property
    def list_count(self):
        """ Number of users registered to attend the event """
        return Registration.objects.filter(event__pk=self.pk, is_on_wait=False).count()

    @property
    def waiting_list_count(self):
        """ Number of users on the waiting list """
        return Registration.objects.filter(event__pk=self.pk, is_on_wait=True).count()

    @property
    def is_past_sign_off_deadline(self):
        return today() >= self.sign_off_deadline

    def has_waiting_list(self):
        return self.has_limit() and (
            self.is_full()
            or Registration.objects.filter(event=self, is_on_wait=True).exists()
        )

    def has_limit(self):
        return self.limit != 0

    def is_full(self):
        return Registration.objects.filter(event=self).count() >= self.limit

    def has_priorities(self):
        return self.registration_priorities.all().exists()

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
                _("Enable signup to add start_date and end time for registration.")
            )

    def check_if_registration_is_not_set(self):
        if self.sign_up and not (
            self.start_registration_at
            and self.end_registration_at
            and self.sign_off_deadline
        ):
            raise ValidationError(
                _("Set start- and end-registration and sign_off_deadline")
            )

    def check_sign_up_and_sign_off_deadline(self):
        if not self.sign_up and self.sign_off_deadline:
            raise ValidationError(_("Enable signup to add deadline."))

    def check_start_time_is_before_end_registration(self):
        if self.start_date < self.end_registration_at:
            raise ValidationError(
                _("End time for registration cannot be after the event start_date.")
            )

    def check_start_registration_is_before_end_registration(self):
        if self.start_registration_at > self.end_registration_at:
            raise ValidationError(
                _("Start time for registration cannot be after end time.")
            )

    def check_start_registration_is_after_start_time(self):
        if self.start_date < self.start_registration_at:
            raise ValidationError(
                _(
                    "Event start_date time for registration cannot be after start_date time."
                )
            )

    def check_end_time_is_before_end_registration(self):
        if self.end_date < self.end_registration_at:
            raise ValidationError(
                _("End time for registration cannot be after the event end_date.")
            )

    def check_start_date_is_before_deadline(self):
        if self.start_date < self.sign_off_deadline:
            raise ValidationError(
                _("End time for sign_off cannot be after the event start_date.")
            )

    def check_start_registration_is_after_deadline(self):
        if self.start_registration_at > self.sign_off_deadline:
            raise ValidationError(
                _(
                    "End time for sign_off cannot be after the event start_registration_at."
                )
            )

    def check_start_time_is_after_end_time(self):
        if self.end_date < self.start_date:
            raise ValidationError(
                _("End date for event cannot be before the event start_date.")
            )


signals.post_save.connect(receiver=send_event_reminders, sender=Event)
