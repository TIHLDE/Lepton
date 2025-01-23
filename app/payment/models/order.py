import uuid

from django.db import models

from app.common.enums import AdminGroup, Groups
from app.common.permissions import (
    BasePermissionModel,
    check_has_access,
    is_admin_user,
    is_index_user,
)
from app.content.models.event import Event
from app.content.models.user import User
from app.group.models.membership import Membership
from app.payment.enums import OrderStatus
from app.util.models import BaseModel


class Order(BaseModel, BasePermissionModel):
    read_access = (Groups.TIHLDE,)
    update_access = (AdminGroup.INDEX,)

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
        if check_has_access(cls.update_access, request):
            return True

        order_id = request.parser_context.get("kwargs", {}).get("pk")
        print(f"Order ID: {order_id}")

        if order_id:
            try:
                order = Order.objects.get(order_id=order_id)
                print(f"Order: {order}")

                if order.event.organizer and order.event.organizer.slug:
                    is_member = Membership.objects.filter(
                        user=request.user,
                        group=order.event.organizer,
                    ).exists()

                    if is_member:
                        print(
                            f"User is a member of the organizer group: {order.event.organizer}"
                        )
                        return True
                    else:
                        print(
                            f"User is not a member of the organizer group: {order.event.organizer}"
                        )
                        return False
            except Order.DoesNotExist:
                return False

        return False

    @classmethod
    def has_destroy_permission(cls, request):
        return False

    @classmethod
    def has_retrieve_permission(cls, request):
        if not request.user:
            return False

        return (
            check_has_access(cls.read_access, request)
            or is_admin_user(request)
            or request.user.memberships_with_events_access.exists()
        )

    @classmethod
    def has_read_permission(cls, request):
        if not request.user:
            return False

        return (
            check_has_access(cls.read_access, request)
            or request.user.memberships_with_events_access.exists()
        )

    @classmethod
    def has_list_permission(cls, request):
        return is_admin_user(request)

    @classmethod
    def has_read_all_permission(cls, request):
        return is_admin_user(request)

    def has_object_update_permission(self, request):
        return self.has_update_permission(request)

    def has_object_destroy_permission(self, _request):
        return False

    def has_object_retrieve_permission(self, request):
        if not request.user:
            return False

        organizer = self.event.organizer

        return (
            self.check_request_user_has_access_through_organizer(
                request.user, organizer
            )
            or is_admin_user(request)
            or self.user == request.user
        )

    def check_request_user_has_access_through_organizer(self, user, organizer):
        # All memberships that have access to events will also have access to orders
        if not organizer:
            return False

        return user.memberships_with_events_access.filter(group=organizer).exists()
