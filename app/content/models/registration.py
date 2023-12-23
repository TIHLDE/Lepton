from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from sentry_sdk import capture_exception

from app.common.enums import StrikeEnum
from app.common.permissions import BasePermissionModel
from app.communication.enums import UserNotificationSettingType
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
from app.content.util.registration_utils import get_payment_expiredate
from app.forms.enums import EventFormType
from app.payment.util.order_utils import check_if_order_is_paid, has_paid_order
from app.util import now
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
    payment_expiredate = models.DateTimeField(null=True, default=None)
    created_by_admin = models.BooleanField(default=False)

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

    def refund_payment_if_exist(self):
        from app.content.util.event_utils import refund_vipps_order

        if not self.event.is_paid_event:
            return

        orders = self.event.orders.filter(user=self.user)

        if has_paid_order(orders):
            for order in orders:
                if check_if_order_is_paid(order):
                    refund_vipps_order(
                        order_id=order.order_id,
                        event=self.event,
                        transaction_text=f"Refund for {self.event.title} - {self.user.first_name} {self.user.last_name}",
                    )
                    self.send_notification_and_mail_for_refund(order)

    def delete(self, *args, **kwargs):
        from app.content.util.event_utils import start_payment_countdown

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

        # TODO: Add this for refund
        # self.refund_payment_if_exist()

        registration = super().delete(*args, **kwargs)
        if moved_registration:
            moved_registration.save()

            if (
                moved_registration.event.is_paid_event
                and not moved_registration.is_on_wait
            ):
                try:
                    start_payment_countdown(
                        moved_registration.event, moved_registration
                    )
                except Exception as countdown_error:
                    capture_exception(countdown_error)
                    moved_registration.delete()

        return registration

    def admin_unregister(self, *args, **kwargs):
        moved_registration = self.move_from_waiting_list_to_queue()
        self.delete_submission_if_exists()
        self.send_unregistered_notification_and_mail()

        super().delete(*args, **kwargs)

        if moved_registration:
            moved_registration.save()

    def save(self, *args, **kwargs):

        if not self.registration_id:
            self.create()

        if (
            self.event.is_full
            and not self.is_on_wait
            and self in self.event.get_waiting_list()
        ):
            raise EventIsFullError

        self.send_notification_and_mail()
        return super().save(*args, **kwargs)

    def create(self):
        if self.event.enforces_previous_strikes and not self.created_by_admin:
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

    def send_unregistered_notification_and_mail(self):
        Notify(
            [self.user],
            f'Du har blitt meldt av "{self.event.title}"',
            UserNotificationSettingType.UNREGISTRATION,
        ).add_paragraph(f"Hei, {self.user.first_name}!").add_paragraph(
            "Den ansvarlige for dette arrangementet har fjernet påmeldingen din."
        ).add_paragraph(
            "Det kan være flere årsaker til dette. Dersom du har spørsmål kan du kontakte den ansvarlige for arrangementet."
        ).add_paragraph(
            "Husk at du må melde deg på igjen hvis du ønsker plass på ventelisten."
        ).add_event_link(
            self.event.pk
        ).send()

    def send_notification_and_mail(self):
        has_not_attended = not self.has_attended
        if not self.is_on_wait and has_not_attended:
            Notify(
                [self.user],
                f'Du har fått plass på "{self.event.title}"',
                UserNotificationSettingType.REGISTRATION,
            ).add_paragraph(f"Hei, {self.user.first_name}!").add_paragraph(
                f"Arrangementet starter {datetime_format(self.event.start_date)} og vil være på {self.event.location}."
            ).add_paragraph(
                f"Du kan melde deg av innen {datetime_format(self.event.sign_off_deadline)}."
            ).add_event_link(
                self.event.pk
            ).send()
        elif self.is_on_wait and has_not_attended:
            Notify(
                [self.user],
                f'Venteliste for "{self.event.title}"',
                UserNotificationSettingType.REGISTRATION,
            ).add_paragraph(f"Hei, {self.user.first_name}!").add_paragraph(
                f"På grunn av stor pågang har du blitt satt på venteliste for {self.event.title}."
            ).add_paragraph(
                "Dersom noen melder seg av, vil du automatisk bli flyttet opp på listen. Du vil få beskjed dersom du får plass på arrangementet."
            ).add_paragraph(
                f"PS. De vanlige reglene for prikker gjelder også for venteliste, husk derfor å melde deg av arrangementet innen {datetime_format(self.event.sign_off_deadline)} dersom du ikke kan møte."
            ).add_event_link(
                self.event.pk
            ).send()

    def send_notification_and_mail_for_refund(self, order):
        Notify(
            [self.user],
            f'Du har blitt meldt av "{self.event.title}" og vil bli refundert',
            UserNotificationSettingType.UNREGISTRATION,
        ).add_paragraph(f"Hei, {self.user.first_name}!").add_paragraph(
            f"Du har blitt meldt av {self.event.title} og vil bli refundert."
        ).add_paragraph(
            "Du vil få pengene tilbake på kontoen din innen 2 til 3 virkedager. I enkelte tilfeller, avhengig av bank, tar det inntil 10 virkedager."
        ).add_paragraph(
            f"Hvis det skulle oppstå noen problemer så kontakt oss på hs@tihlde.org. Ditt ordrenummer er {order.order_id}."
        ).send()

    def should_swap_with_non_prioritized_user(self):
        return (
            self.is_on_wait
            and self.is_prioritized
            and self.event.has_priorities()
            and self.event.is_full
        )

    @property
    def is_prioritized(self):
        if self.created_by_admin:
            return True

        if self.user.number_of_strikes >= 3 and self.event.enforces_previous_strikes:
            return False

        user_groups = set(self.user.group_members.values_list("slug", flat=True))
        pools = self.event.priority_pools.prefetch_related("groups").all()

        for pool in pools:
            pool_groups = set(pool.groups.values_list("slug", flat=True))
            is_in_priority_pool = pool_groups.issubset(user_groups) and len(pool_groups)

            if is_in_priority_pool:
                return True

        return False

    @property
    def wait_queue_number(self):
        """
        Returns the number of people in front of the user in the waiting list.
        """
        waiting_list_count = (
            self.event.get_waiting_list()
            .order_by("-created_at")
            .filter(created_at__lte=self.created_at)
            .count()
        )

        if waiting_list_count == 0 or not self.is_on_wait:
            return None

        return waiting_list_count

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

            if self.event.is_paid_event:
                registration_move_to_queue.payment_expiredate = get_payment_expiredate(
                    self.event
                )

            return registration_move_to_queue

    def move_from_queue_to_waiting_list(self):
        registrations_in_queue = self.event.get_participants().order_by("-created_at")

        if registrations_in_queue:
            registration_move_to_waiting_list = next(
                (
                    registration
                    for registration in registrations_in_queue
                    if not registration.is_prioritized
                ),
                registrations_in_queue[0],
            )
            registration_move_to_waiting_list.is_on_wait = True
            return registration_move_to_waiting_list

    def clean(self):
        """
        Validates model fields. Is called upon instance save.

        :raises ValidationError if the event or queue is closed.
        """
        if self.event.closed and not self.created_by_admin:
            raise ValidationError(
                "Dette arrangementet er stengt du kan derfor ikke melde deg på"
            )
        if not self.event.sign_up:
            raise ValidationError("Påmelding er ikke mulig")
        if not self.registration_id and not self.created_by_admin:
            self.validate_start_and_end_registration_time()
        if not self.check_answered_submission() and not self.created_by_admin:
            raise ValidationError(
                "Du må svare på spørreskjemaet før du kan melde deg på arrangementet"
            )
        if (
            self.event.priority_pools
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
