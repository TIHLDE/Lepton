<<<<<<< HEAD
import uuid

=======
>>>>>>> 4255020 (added Order model, view and serializer)
from django.db import models
from app.common.enums import AdminGroup
from app.payment.enums import OrderStatus
from app.content.models.user import User
<<<<<<< HEAD
from app.util.models import BaseModel, BasePermissionModel
=======
from app.util.models import BaseModel
from app.common.permissions import BasePermissionModel
>>>>>>> 4255020 (added Order model, view and serializer)


class Order(BaseModel, BasePermissionModel):
    access = AdminGroup.admin()
    order_id = models.CharField(primary_key=True, max_length=24)
    user_id = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
<<<<<<< HEAD
    status = models.CharField(choices=OrderStatus.choices, default=OrderStatus.INITIATE, max_length=15)
=======
    status = models.CharField(choices=OrderStatus.choices, default=OrderStatus.INITIATE, max_length=16)
>>>>>>> 4255020 (added Order model, view and serializer)
    expire_date = models.DateTimeField()

    class Meta:
        verbose_name_plural = "Orders"
        ordering = ("-created_at", )
    
        def __str__(self):
            return f"{self.order_id} {self.user_id} {self.status} {self.expire_date}"