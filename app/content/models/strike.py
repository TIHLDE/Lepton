import uuid
from datetime import timedelta

from django.db import models

from app.content.models import Event, User
from app.util.models import BaseModel
from app.util.utils import today

STRIKE_DURATION_IN_DAYS = 20


class Strike(BaseModel):
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, serialize=False,
    )
    description = models.CharField(max_length=200)
    strike_size = models.IntegerField(default=1)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="strikes")
    event = models.ForeignKey(
        Event, on_delete=models.SET_NULL, blank=True, null=True, related_name="strikes"
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_strikes",
    )

    class Meta:
        verbose_name = "Strike"
        verbose_name_plural = "Strikes"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.description} - {self.strike_size}"

    @property
    def active(self):
        return self.expires_at >= today()

    @property
    def expires_at(self):
        return self.created_at + timedelta(days=STRIKE_DURATION_IN_DAYS)
