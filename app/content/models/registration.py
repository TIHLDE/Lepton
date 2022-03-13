from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from app.common.enums import StrikeEnum
from app.common.permissions import BasePermissionModel
from app.communication.notifier import Notify
from app.content.exceptions import (
    EventIsFullError,
    EventSignOffDeadlineHasPassed,
    StrikeError,
    UnansweredFormError,
)
from app.content.models.event import Event
from app.content.models.strike import create_strike
from app.content.models.user import User
from app.forms.enums import EventFormType
from app.util import EnumUtils, now
from app.util.mail_creator import MailCreator
from app.util.models import BaseModel
from app.util.utils import datetime_format


class Registration(BaseModel, BasePermissionModel):

    registration_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="registrations"
    )
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="registrations"
    )

    is_on_wait = models.BooleanField(default=False, verbose_name="waiting list")
    has_attended = models.BooleanField(default=False)
    allow_photo = models.BooleanField(default=True)

    class Meta:
        ordering = ("event", "created_at", "is_on_wait")
        unique_together = ("user", "event")
        verbose_name = "Registration"
        verbose_name_plural = "Registrations"

    @classmethod
    def has_retrieve_permission(cls, request):
        return True

    @classmethod
    def has_list_permission(cls, request):
        return cls.has_event_permission(cls, request)

    @classmethod
    def has_write_permission(cls, request):
        return bool(request.user)

    def has_event_permission(self, request):
        if request.user is None:
            return False

        event = Event.objects.get(id=request.parser_context["kwargs"]["event_id"])
        return event.has_object_write_permission(request)

    def is_own_registration(self, request):
        return self.user.user_id == request.id

    def has_object_update_permission(self, request):
        return self.has_event_permission(request)

    def has_object_destroy_permission(self, request):
        return self.is_own_registration(request) or self.has_event_permission(request)

    def has_object_retrieve_permission(self, request):
        return self.is_own_registration(request) or self.has_event_permission(request)

    def __str__(self):
        return f"{self.user.email} - {self.event.title} (on wait: {self.is_on_wait})"

    def delete_submission_if_exists(self):
        from app.forms.models.forms import EventForm, Submission

        event_form = EventForm.objects.filter(
            event=self.event, type=EventFormType.SURVEY
        )[:1]
        Submission.objects.filter(form=event_form, user=self.user).delete()

    def delete(self, *args, **kwargs):
        moved_registration = None
        if not self.is_on_wait:
            if self.event.is_past_sign_off_deadline:
                if self.event.is_two_hours_before_event_start():
                    raise EventSignOffDeadlineHasPassed(
                        "Kan ikke melde av brukeren etter to timer før arrangementstart"
                    )
                if self.event.can_cause_strikes:
                    create_strike(str(StrikeEnum.PAST_DEADLINE), self.user, self.event)
            moved_registration = self.move_from_waiting_list_to_queue()

        self.delete_submission_if_exists()
        registration = super().delete(*args, **kwargs)
        if moved_registration:
            moved_registration.save()
        return registration

    def admin_unregister(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.registration_id:
            self.create()
        self.send_notification_and_mail()

        if (
            self.event.is_full
            and not self.is_on_wait
            and self in self.event.get_waiting_list()
        ):
            raise EventIsFullError

        return super().save(*args, **kwargs)

    def create(self):
        if self.event.enforces_previous_strikes:
            self._abort_for_unanswered_evaluations()
            self.strike_handler()

        self.clean()
        self.is_on_wait = self.event.is_full

        if self.should_swap_with_non_prioritized_user():
            self.swap_users()

    def _abort_for_unanswered_evaluations(self):
        if self.user.has_unanswered_evaluations():
            raise UnansweredFormError()

    def strike_handler(self):
        number_of_strikes = self.user.number_of_strikes
        if number_of_strikes >= 1:
            hours_offset = 3
            if number_of_strikes >= 2:
                hours_offset = 12
            if not now() >= self.event.start_registration_at + timedelta(
                hours=hours_offset
            ):
                raise StrikeError(
                    f"Du har for mange prikker og kan derfor ikke melde deg på arrangementet før {hours_offset} timer etter påmeldingsstart."
                )

    def check_answered_submission(self):
        from app.forms.models import EventForm

        form = EventForm.objects.filter(event=self.event, type=EventFormType.SURVEY)
        submission = self.get_submissions(type=EventFormType.SURVEY)
        return not form.exists() or submission.exists()

    def send_notification_and_mail(self):
        has_not_attended = not self.has_attended
        if not self.is_on_wait and has_not_attended:
            description = [
                f"Du er påmeldt {self.event.title}!",
                f"Arrangementet starter {datetime_format(self.event.start_date)} og vil være på {self.event.location}.",
                f"Du kan melde deg av innen {datetime_format(self.event.sign_off_deadline)}.",
            ]
            Notify([self.user], f"Du har fått plass på {self.event.title}").send_email(
                MailCreator("Du er påmeldt")
                .add_paragraph(f"Hei {self.user.first_name}!")
                .add_paragraph(description[0])
                .add_paragraph(description[1])
                .add_paragraph(description[2])
                .add_event_button(self.event.pk)
                .generate_string()
            ).send_notification(
                description=" ".join(description), link=self.event.website_url
            )
        elif self.is_on_wait and has_not_attended:
            description = [
                f"På grunn av stor pågang har du blitt satt på venteliste for {self.event.title}.",
                "Dersom noen melder seg av vil du automatisk bli flyttet opp på listen. Du vil få beskjed dersom du får plass på arrangementet.",
                f"PS. De vanlige reglene for prikker gjelder også for venteliste, husk derfor å melde deg av arrangementet innen {datetime_format(self.event.sign_off_deadline)} dersom du ikke kan møte.",
            ]
            Notify([self.user], f"Venteliste for {self.event.title}").send_email(
                MailCreator("Du er på ventelisten")
                .add_paragraph(f"Hei {self.user.first_name}!")
                .add_paragraph(description[0])
                .add_paragraph(description[1])
                .add_paragraph(description[2])
                .add_event_button(self.event.pk)
                .generate_string()
            ).send_notification(
                description=" ".join(description),
                link=self.event.website_url,
            )

    def should_swap_with_non_prioritized_user(self):
        return (
            self.is_on_wait
            and self.is_prioritized
            and self.event.has_priorities()
            and self.event.is_full
        )

    @property
    def is_prioritized(self):
        if self.user.number_of_strikes >= 3:
            return False

        user_class, user_study = EnumUtils.get_user_enums(**self.user.__dict__)
        user_query = Q(user_class=user_class, user_study=user_study)

        user_groups = set(self.user.group_members.values_list("slug", flat=True))
        pools = self.event.priority_pools.prefetch_related("groups").all()

        for pool in pools:
            pool_groups = set(pool.groups.values_list("slug", flat=True))
            is_in_priority_pool = pool_groups.issubset(user_groups) and len(pool_groups)

            if is_in_priority_pool:
                return True

        return self.event.registration_priorities.filter(user_query).exists()

    def swap_users(self):
        """Swaps a user with a spot with a prioritized user, if such user exists"""
        for registration in self.event.get_participants().order_by("-created_at"):
            if not registration.is_prioritized:
                return self.swap_places_with(registration)

    def swap_places_with(self, other_registration):
        """Puts own self on the list and other_registration on wait"""
        other_registration.is_on_wait = True
        other_registration.save()
        self.is_on_wait = False

    def move_from_waiting_list_to_queue(self):
        registrations_in_waiting_list = self.event.get_waiting_list().order_by(
            "created_at"
        )
        if registrations_in_waiting_list:
            registration_move_to_queue = next(
                (
                    registration
                    for registration in registrations_in_waiting_list
                    if registration.is_prioritized
                ),
                registrations_in_waiting_list[0],
            )
            registration_move_to_queue.is_on_wait = False
            return registration_move_to_queue

    def clean(self):
        """
        Validates model fields. Is called upon instance save.

        :raises ValidationError if the event or queue is closed.
        """
        if self.event.closed:
            raise ValidationError(
                "Dette arrangementet er stengt du kan derfor ikke melde deg på"
            )
        if not self.event.sign_up:
            raise ValidationError("Påmelding er ikke mulig")
        if not self.registration_id:
            self.validate_start_and_end_registration_time()
        if not self.check_answered_submission():
            raise ValidationError(
                "Du må svare på spørreskjemaet før du kan melde deg på arrangementet"
            )
        if (
            self.event.registration_priorities
            and self.event.only_allow_prioritized
            and not self.is_prioritized
        ):
            raise ValidationError(
                "Dette arrangementet er kun åpent for de prioriterte gruppene"
            )

    def validate_start_and_end_registration_time(self):
        self.check_registration_has_started()
        self.check_registration_has_ended()

    def check_registration_has_started(self):
        if self.event.start_registration_at > now():
            raise ValidationError("Påmeldingen har ikke åpnet enda")

    def check_registration_has_ended(self):
        if self.event.end_registration_at < now():
            raise ValidationError("Påmeldingsfristen har passert")

    def get_submissions(self, type=None):
        from app.forms.models import EventForm, Submission

        query = Q(event=self.event)

        if type:
            query &= Q(type=type)

        forms = EventForm.objects.filter(query)
        return Submission.objects.filter(form__in=forms, user=self.user)
