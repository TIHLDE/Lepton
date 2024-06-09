import uuid

from django.db import models

from app.common.enums import AdminGroup, Groups
from app.common.permissions import (
    BasePermissionModel,
    is_admin_user,
    check_has_access
)
from app.content.models.event import Event
from app.content.models.user import User
from app.payment.enums import OrderStatus
from app.util.models import BaseModel


class Order(BaseModel, BasePermissionModel):
    read_access = AdminGroup.admin
    write_access = (Groups.TIHLDE, )

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
    def has_update_permission(cls, request):
        return False

    @classmethod
    def has_destroy_permission(cls, request):
        return False

    @classmethod
    def has_retrieve_permission(cls, request):
        return (
            (
                check_has_access(cls.read_access, request)
                or request.user.memberships_with_events_access.exists()
            )
        )
    
    @classmethod
    def has_retrieve_all_permission(cls, request):
        return is_admin_user(request)

    @classmethod
    def has_read_permission(cls, request):
        return (
            (
                check_has_access(cls.read_access, request)
                or request.user.memberships_with_events_access.exists()
            )
        )

    @classmethod
    def has_read_all_permission(cls, request):
        return is_admin_user(request)
    
    @classmethod
    def has_create_permission(cls, request):
        return cls.has_write_permission(request)

    def has_object_update_permission(self, request):
        return False

    def has_object_destroy_permission(self, request):
        return False

    def has_object_retrieve_permission(self, request):
        organizer = self.event.organizer
        if not organizer:
            return False
        
        return self.check_request_user_has_access_through_organizer(request.user, organizer) or check_has_access(self.read_access, request)
    
    def check_request_user_has_access_through_organizer(self, user, organizer):
        # All memberships that have access to events will also have access to orders
        return user.memberships_with_events_access.filter(group=organizer).exists()
