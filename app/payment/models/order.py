import uuid

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
    user = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="orders"
    )
    event = models.ForeignKey(
        Event, null=True, on_delete=models.SET_NULL, related_name="orders"
    )
    status = models.CharField(
        choices=OrderStatus.choices, default=OrderStatus.INITIATE, max_length=16
    )
    expire_date = models.DateTimeField()
    payment_link = models.URLField(max_length=2000)

    class Meta:
        verbose_name_plural = "Orders"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.status} - {self.created_at}"

    @property
    def expired(self):
        return now() >= self.expire_date
