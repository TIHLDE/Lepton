from django.db import models

from app.common.enums import AdminGroup
from app.content.models.event import Event
from app.util.models import BaseModel


class PaidEvent(BaseModel):
    write_access = AdminGroup.admin()

    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name="paid_information",
        primary_key=True,
    )
    price = models.DecimalField(max_digits=6, decimal_places=2)
    paytime = models.TimeField()

    class Meta:
        verbose_name_plural = "Paid_events"

    def __str__(self):
        return f"Price: {self.price}"
