from app.util.models import BaseModel
from app.common.enums import AdminGroup
from app.content.models.event import Event
from django.db import models


class PaidEvent(BaseModel):
    write_access = AdminGroup.admin()

    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name="paid_information", primary_key=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        verbose_name_plural = "Paid_events"

    def __str__(self):
        return f"Price: {self.price}"
