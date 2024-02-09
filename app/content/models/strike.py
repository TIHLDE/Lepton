import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.db.models.aggregates import Sum

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel, check_has_access
from app.communication.enums import UserNotificationSettingType
from app.content.models import Event
from app.util.models import BaseModel
from app.util.utils import getTimezone, now


class Holiday:
    def __init__(self, start, end):
        self.start = start
        self.end = end


STRIKE_DURATION_IN_DAYS = 20

SUMMER = Holiday((5, 10), (8, 15))
WINTER = Holiday((11, 29), (1, 9))

HOLIDAYS = (SUMMER, WINTER)


class StrikeQueryset(models.QuerySet):
    def active(self, *args, **kwargs):
        active_filter = {
            "created_at__gte": now() - timedelta(days=STRIKE_DURATION_IN_DAYS),
            **kwargs,
        }
        return self.filter(*args, **active_filter)

    def sum_active(self):
        sum_active_strikes = (
            self.active().aggregate(Sum("strike_size")).get("strike_size__sum")
        )
        return sum_active_strikes or 0


class Strike(BaseModel, BasePermissionModel):
    write_access = [
        AdminGroup.HS,
        AdminGroup.INDEX,
        AdminGroup.NOK,
        AdminGroup.SOSIALEN,
    ]

    read_access = write_access

    id = models.UUIDField(
        auto_created=True,
        primary_key=True,
        default=uuid.uuid4,
        serialize=False,
    )
    description = models.CharField(max_length=200)
    strike_size = models.IntegerField(default=1)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="strikes"
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="strikes",
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_strikes",
    )

    objects = StrikeQueryset.as_manager()

    class Meta:
        verbose_name = "Strike"
        verbose_name_plural = "Strikes"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.description} - {self.strike_size}"

    def save(self, *args, **kwargs):
        if self.created_at is None:
            from app.communication.notifier import Notify

            Notify(
                [self.user], "Du har fått en prikk", UserNotificationSettingType.STRIKE
            ).add_paragraph(f"Hei, {self.user.first_name}!").add_paragraph(
                self.description
            ).add_paragraph(
                "Prikken varer i 20 dager. Ta kontakt med arrangøren om du er uenig. Konsekvenser kan sees i arrangementsreglene. Du kan finne dine aktive prikker og mer info om dem i profilen."
            ).send()
        super(Strike, self).save(*args, **kwargs)

    @property
    def active(self):
        return self.expires_at >= now()

    @property
    def expires_at(self):

        expired_date = self.created_at + timedelta(STRIKE_DURATION_IN_DAYS)

        for holiday in HOLIDAYS:

            start = holiday.start
            end = holiday.end

            start_date = datetime(
                self.created_at.year, start[0], start[1], tzinfo=getTimezone()
            )
            end_date = datetime(
                self.created_at.year, end[0], end[1], tzinfo=getTimezone()
            )

            if end_date < start_date:
                end_date = end_date.replace(year=end_date.year + 1)

            if expired_date > start_date and self.created_at < end_date:
                smallest_difference = min(
                    (end_date - start_date), (end_date - self.created_at)
                )
                expired_date += smallest_difference + timedelta(days=1)
                break

        return expired_date.astimezone(getTimezone())

    @classmethod
    def has_write_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_destroy_permission(cls, request):
        return check_has_access(AdminGroup.admin(), request)
    
    @classmethod
    def has_read_permission(cls, request):
        return check_has_access(cls.read_access, request)
    
    @classmethod
    def has_retrieve_permission(cls, request):
        return check_has_access(cls.read_access, request)
    
    @classmethod
    def has_update_permission(cls, request):
        return check_has_access(cls.write_access, request)

    def has_object_read_permission(self, request):
        return self.user.user_id == request.id or check_has_access(
            self.read_access, request
        )


def create_strike(enum, user, event=None, creator=None):
    return Strike.objects.create(
        description=get_strike_description(enum),
        strike_size=get_strike_strike_size(enum),
        user=user,
        event=event,
        creator=creator,
    )


StrikeDescription = {
    "PAST_DEADLINE": [
        "Du har fått prikk fordi du meldte deg av etter avmeldingsfristen",
        1,
    ],
    "NO_SHOW": ["Du har fått prikk fordi du ikke møtte på et arrangement", 2],
    "LATE": ["Du har fått prikk fordi du møtte sent på et arrangement", 1],
    "BAD_BEHAVIOR": [
        "Du har fått prikk på grunn av upassende oppførsel på et arrangementet",
        1,
    ],
    "EVAL_FORM": [
        "Du har fått prikk fordi du ikke svarte på evalueringsskjema til et arrangement",
        3,
    ],
}


def get_strike_description(enum):
    return StrikeDescription[enum][0]


def get_strike_strike_size(enum):
    return StrikeDescription[enum][1]
