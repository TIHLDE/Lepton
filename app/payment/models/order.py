from django.db import models
from app.common.enums import AdminGroup
from app.payment.enums import OrderStatus
from app.content.models.user import User
from app.util.models import BaseModel
from app.common.permissions import BasePermissionModel


class Order(BaseModel, BasePermissionModel):
    access = AdminGroup.admin()
    order_id = models.CharField(primary_key=True, max_length=24)
    user_id = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(choices=OrderStatus.choices, default=OrderStatus.INITIATE, max_length=16)
    expire_date = models.DateTimeField()

    class Meta:
        verbose_name_plural = "Orders"
        ordering = ("-created_at", )
    
        def __str__(self):
            return f"{self.order_id} {self.user_id} {self.status} {self.expire_date}"