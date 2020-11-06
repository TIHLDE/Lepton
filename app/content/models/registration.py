from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from app.content.exceptions import EventSignOffDeadlineHasPassed
from app.content.models.user import User
from app.util import EnumUtils, today
from app.util.mailer import send_event_verification, send_event_waitlist
from app.util.models import BaseModel


class Registration(BaseModel):
    """ Model for user registration for an event """

    registration_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="registrations"
    )
    event = models.ForeignKey(
        "Event", on_delete=models.CASCADE, related_name="registrations"
    )

    is_on_wait = models.BooleanField(default=False, verbose_name="waiting list")
    has_attended = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True, verbose_name="Signed up on")
    allow_photo = models.BooleanField(default=True)

    class Meta:
        ordering = ("event", "is_on_wait", "created_at")
        unique_together = ("user", "event")
        verbose_name = "Registration"
        verbose_name_plural = "Registrations"

    def __str__(self):
        return (
            f"{self.user.email} - is to attend {self.event} and is "
            f'{"on the waiting list" if self.is_on_wait else "on the list"}'
        )

    def delete(self, *args, **kwargs):
        if self.event.is_past_sign_off_deadline:
            raise EventSignOffDeadlineHasPassed(
                _("Cannot sign user off after sign off deadline has passed")
            )
        if not self.is_on_wait:
            self.move_from_waiting_list_to_queue()

        return super().delete(*args, **kwargs)

    def admin_unregister(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        """ Determines whether the object is being created or updated and acts accordingly """
        if not self.registration_id:
            self.create()
        self.send_notification_and_mail()
        return super(Registration, self).save(*args, **kwargs)

    def create(self):
        """ Determines whether user is on the waiting list or not when the instance is created. """
        self.clean()
        self.is_on_wait = self.event.is_full

        if self.should_swap_with_non_prioritized_user():
            self.swap_users()

    def send_notification_and_mail(self):
        has_not_attended = not self.has_attended
        if not self.is_on_wait and has_not_attended:
            send_event_verification(self)
        elif self.is_on_wait and has_not_attended:
            send_event_waitlist(self)

    def should_swap_with_non_prioritized_user(self):
        return (
            self.is_on_wait
            and self.is_prioritized
            and self.event.has_priorities()
            and self.event.is_full
        )

    @property
    def is_prioritized(self):
        user_class, user_study = EnumUtils.get_user_enums(**self.user.__dict__)
        return self.event.registration_priorities.filter(
            user_class=user_class, user_study=user_study
        ).exists()

    def swap_users(self):
        """ Swaps a user with a spot with a prioritized user, if such user exists """
        for registration in self.event.get_queue().order_by("-created_at"):
            if not registration.is_prioritized:
                return self.swap_places_with(registration)

    def swap_places_with(self, other_registration):
        """ Puts own self on the list and other_registration on wait """
        other_registration.is_on_wait = True
        other_registration.save()
        self.is_on_wait = False

    def move_from_waiting_list_to_queue(self):
        registrations = self.event.get_waiting_list().order_by("created_at")
        registration_move_to_queue = next(
            (
                registration
                for registration in registrations
                if registration.is_prioritized
            ),
            registrations[0],
        )
        registration_move_to_queue.is_on_wait = False
        registration_move_to_queue.save()

    def clean(self):
        """
        Validates model fields. Is called upon instance save.

        :raises ValidationError if the event or queue is closed.
        """
        if self.event.closed:
            raise ValidationError(_("The queue for this event is closed"))
        if not self.event.sign_up:
            raise ValidationError(_("Sign up is not possible"))
        if not self.registration_id:
            self.validate_start_and_end_registration_time()

    def validate_start_and_end_registration_time(self):
        self.check_registration_has_started()
        self.check_registration_has_ended()

    def check_registration_has_started(self):
        if self.event.start_registration_at > today():
            raise ValidationError(
                _("The registration for this event has not started yet.")
            )

    def check_registration_has_ended(self):
        if self.event.end_registration_at < today():
            raise ValidationError(_("The registration for this event has ended."))
