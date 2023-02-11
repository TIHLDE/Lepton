from django.db import models
from app.common.enums import AdminGroup
from app.content.models.event import Event
from app.payment.enums import OrderStatus
from app.content.models.user import User
from app.payment.models.paid_event import PaidEvent
from app.util.models import BaseModel
from app.common.permissions import BasePermissionModel
from app.util.utils import now, yesterday



class Order(BaseModel, BasePermissionModel):
    access = AdminGroup.admin()
    order_id = models.CharField(primary_key=True, max_length=24)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(choices=OrderStatus.choices, default=OrderStatus.INITIATE, max_length=16)
    expire_date = models.DateTimeField()

    class Meta:
        verbose_name_plural = "Orders"
        ordering = ("-expire_date", )

        def __str__(self):
            return f"{self.order_id} {self.user} {self.event} {self.status} {self.expire_date}"

    @property
    def expired(self):
        return now() >= self.expire_date
