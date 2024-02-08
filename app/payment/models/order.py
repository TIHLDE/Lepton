import uuid

from django.db import models

from app.common.enums import AdminGroup, Groups
from app.common.permissions import (
    BasePermissionModel,
    check_has_access,
    is_admin_group_user,
    is_admin_user,
    is_index_user,
)
from app.content.models.event import Event
from app.content.models.user import User
from app.payment.enums import OrderStatus
from app.util.models import BaseModel


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
    payment_link = models.URLField(max_length=2000)

    class Meta:
        verbose_name_plural = "Orders"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user} - {self.event.title if self.event else ['slettet']} - {self.status} - {self.created_at}"

    @classmethod
    def has_create_permission(cls, request):
        return True

    @classmethod
    def has_update_permission(cls, request):
        return is_admin_user(request)

    @classmethod
    def has_destroy_permission(cls, request):
        return is_index_user(request)

    @classmethod
    def has_retrieve_permission(cls, request):
        return is_admin_group_user(request)

    @classmethod
    def has_read_permission(cls, request):
        return is_admin_group_user(request)

    def has_object_read_permission(self, request):
        return self.has_read_permission(request)

    def has_object_update_permission(self, request):
        return self.has_update_permission(request)

    def has_object_destroy_permission(self, request):
        return self.has_destroy_permission(request)

    def has_object_retrieve_permission(self, request):
        return self.has_retrieve_permission(request)
