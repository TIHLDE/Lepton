import uuid
from datetime import datetime, timedelta

from django.db import models

from app.content.models import Event, User
from app.util.models import BaseModel
from app.util.utils import today


class Strike(BaseModel):
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, serialize=False,
    )
    description = models.CharField(max_length=200)
    expires_at = models.DateTimeField()
    nr_of_strikes = models.IntegerField(default=1)

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
        return f"{self.user.first_name} {self.user.last_name} - {self.description} - {self.nr_of_strikes}"

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    @property
    def active(self):
        return self.expires_at >= today()
