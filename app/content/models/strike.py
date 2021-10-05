import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models.aggregates import Sum

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel
from app.util.utils import today

STRIKE_DURATION_IN_DAYS = 20


class StrikeQueryset(models.QuerySet):
    def active(self):
        return self.filter(
            created_at__lte=today(),
            created_at__gte=today() - timedelta(days=STRIKE_DURATION_IN_DAYS),
        )

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
        # TODO: Kjør når prikksystem er lansert "offisielt"
        # if self.created_at is None:
        #     from app.util.mail_creator import MailCreator
        #     from app.util.notifier import Notify

        #     Notify(self.user, "Du har fått en prikk").send_email(
        #         MailCreator("Du har fått en prikk")
        #         .add_paragraph(f"Hei {self.user.first_name}!")
        #         .add_paragraph(self.description)
        #         .generate_string()
        #     ).send_notification(
        #         description=self.description,
        #     )
        super(Strike, self).save(*args, **kwargs)

    @property
    def active(self):
        return self.expires_at >= today()

    @property
    def expires_at(self):
        return self.created_at + timedelta(days=STRIKE_DURATION_IN_DAYS)


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
