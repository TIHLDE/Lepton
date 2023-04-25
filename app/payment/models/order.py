import uuid
from datetime import timedelta

from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.content.models.event import Event
from app.content.models.user import User
from app.payment.enums import OrderStatus
from app.util.models import BaseModel
from app.util.utils import now


class Order(BaseModel, BasePermissionModel):
    access = AdminGroup.admin()
    order_id = models.UUIDField(
        auto_created=True, default=uuid.uuid4, primary_key=True, serialize=False
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(
        choices=OrderStatus.choices, default=OrderStatus.INITIATE, max_length=16
    )
    expire_date = models.DateTimeField(default=now() + timedelta(minutes=60))
    payment_link = models.URLField(max_length=2000)

    class Meta:
        verbose_name_plural = "Orders"
        ordering = ("-created_at",)

        def __str__(self):
            return f"{self.order_id} {self.user} {self.event} {self.status} {self.expire_date}"

    @property
    def expired(self):
        return now() >= self.expire_date
