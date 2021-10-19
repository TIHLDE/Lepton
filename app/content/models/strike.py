import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.aggregates import Sum

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel, check_has_access
from app.util.models import BaseModel
from app.util.utils import today

STRIKE_DURATION_IN_DAYS = 20


def get_active_strikes_query():
    return Q(
        # TODO: Remove the "+ timedelta(days=1)" after standarizing timezones
        created_at__lte=today() + timedelta(days=1),
        created_at__gte=today() - timedelta(days=STRIKE_DURATION_IN_DAYS),
    )


class StrikeQueryset(models.QuerySet):
    def active(self, *args, **kwargs):
        return self.filter(get_active_strikes_query(), *args, **kwargs)

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
        auto_created=True, primary_key=True, default=uuid.uuid4, serialize=False,
    )
    description = models.CharField(max_length=200)
    strike_size = models.IntegerField(default=1)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="strikes"
    )
    event = models.ForeignKey(
        "content.Event",
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

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.description} - {self.strike_size}"

    def save(self, *args, **kwargs):
        if self.created_at is None:
            from app.util.mail_creator import MailCreator
            from app.util.notifier import Notify

            strike_info = "Prikken varer i 20 dager. Ta kontakt med arrangøren om du er uenig. Konsekvenser kan sees i arrangementsreglene. Du kan finne dine aktive prikker og mer info om dem i profilen."

            Notify([self.user], "Du har fått en prikk").send_email(
                MailCreator("Du har fått en prikk")
                .add_paragraph(f"Hei {self.user.first_name}!")
                .add_paragraph(self.description)
                .add_paragraph(strike_info)
                .generate_string()
            ).send_notification(description=f"{self.description}\n{strike_info}",)
        super(Strike, self).save(*args, **kwargs)

    @property
    def active(self):
        return self.expires_at >= today()

    @property
    def expires_at(self):
        return self.created_at + timedelta(days=STRIKE_DURATION_IN_DAYS)

    @classmethod
    def has_destroy_permission(cls, request):
        return check_has_access(AdminGroup.admin(), request)

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
