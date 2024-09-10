import uuid
from django.db import models

from app.common.enums import AdminGroup, Groups, MembershipType
from app.common.permissions import BasePermissionModel, check_has_access
from app.util.models import BaseModel
from app.kontres.enums import ReservationStateEnum
from app.kontres.models import BookableItem
from app.content.models import User
from app.group.models import Group, Membership
from app.communication.notifier import Notify
from app.communication.enums import UserNotificationSettingType


class Reservation(BaseModel, BasePermissionModel):
    write_access = [Groups.TIHLDE]
    read_access = [Groups.TIHLDE]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="reservations",
        null=True,
        blank=False,
    )
    bookable_item = models.ForeignKey(
        BookableItem,
        on_delete=models.SET_NULL,
        related_name="reservations",
        null=True,
        blank=False,
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    state = models.CharField(
        max_length=15,
        choices=ReservationStateEnum.choices,
        default=ReservationStateEnum.PENDING,
    )
    reason = models.TextField(blank=True)
    description = models.TextField(blank=True)
    accepted_rules = models.BooleanField(default=True)
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name="reservations",
        null=True,
        blank=True,
    )
    serves_alcohol = models.BooleanField(default=False)
    sober_watch = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="sober_watch_reservations",
        null=True,
        blank=True,
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="approved_reservations",
        null=True,
        blank=True,
    )

    def has_object_update_permission(self, request):
        allowed_groups = [AdminGroup.INDEX, AdminGroup.HS]
        is_admin = check_has_access(allowed_groups, request)
        is_author = self.author == request.user

        if 'state' in request.data:
            if not is_admin:
                return False

        if not is_admin and self.state == ReservationStateEnum.CONFIRMED:
            return False

        if is_admin or is_author:
            return True

        return False

    def has_object_destroy_permission(self, request):
        allowed_groups = [AdminGroup.INDEX, AdminGroup.HS]
        is_admin = check_has_access(allowed_groups, request)
        is_author = self.author == request.user

        if not is_admin and self.state == ReservationStateEnum.CONFIRMED:
            return False

        return is_admin or is_author

    def notify_admins_new_reservation(self):
        formatted_start_time = self.start_time.strftime("%d/%m %H:%M")

        leader_membership = Membership.objects.filter(
            group=Group.objects.get(pk="kontkom"), membership_type=MembershipType.LEADER
        ).first()

        if leader_membership is None:
            return

        notification_message = (
            f"En ny reservasjon er opprettet for {self.bookable_item.name}, "
            f"planlagt til {formatted_start_time}."
        )

        Notify(
            users=[leader_membership.user],
            title="Ny Reservasjon Laget",
            notification_type=UserNotificationSettingType.RESERVATION_NEW,
        ).add_paragraph(notification_message).send()

    def notify_approved(self):
        formatted_date_time = self.start_time.strftime("%d/%m %H:%M")
        Notify(
            [self.author],
            f'Reservasjonssøknad for "{self.bookable_item.name} er godkjent."',
            UserNotificationSettingType.RESERVATION_APPROVED,
        ).add_paragraph(
            f"Hei, {self.author.first_name}! Din søknad for å reservere "
            f"{self.bookable_item.name}, den {formatted_date_time} har blitt godkjent."
        ).send()

    def notify_denied(self):
        formatted_date_time = self.start_time.strftime("%d/%m %H:%M")
        Notify(
            [self.author],
            f'Reservasjonssøknad for "{self.bookable_item.name}" er avslått.',
            UserNotificationSettingType.RESERVATION_CANCELLED,
        ).add_paragraph(
        (
            f'Hei, {self.author.first_name}! Din søknad for å reservere {self.bookable_item.name}, den '
            f'{formatted_date_time} har blitt avslått. Du kan ta kontakt med Kontor og Kiosk dersom du lurer på noe ifm. dette.'
        )
        ).send()
