import uuid

from django.db import models

from app.common.enums import AdminGroup, Groups
from app.common.permissions import BasePermissionModel, check_has_access
from app.content.models import User
from app.kontres.enums import ReservationStateEnum
from app.kontres.models.bookable_item import BookableItem
from app.util.models import BaseModel


class Reservation(BaseModel, BasePermissionModel):
    read_access = [Groups.TIHLDE]
    write_access = [Groups.TIHLDE]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reservations"
    )
    bookable_item = models.ForeignKey(
        BookableItem, on_delete=models.PROTECT, related_name="reservations"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    state = models.CharField(
        max_length=15,
        choices=ReservationStateEnum.choices,
        default=ReservationStateEnum.PENDING,
    )
    description = models.TextField(blank=True)
    accepted_rules = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.state} - Reservation request by {self.author.first_name} {self.author.last_name} to book {self.bookable_item.name}. Created at {self.created_at}"

    @classmethod
    def has_read_permission(cls, request):
        return check_has_access(cls.read_access, request)

    @classmethod
    def has_retrieve_permission(cls, request):
        return check_has_access(cls.read_access, request)

    @classmethod
    def has_update_permission(cls, request):
        return check_has_access(cls.write_access, request)

    def has_object_destroy_permission(self, request):
        is_owner = self.author == request.user
        is_admin = check_has_access([AdminGroup.INDEX, AdminGroup.HS], request)
        return is_owner or is_admin

    @classmethod
    def has_create_permission(cls, request):
        return check_has_access(cls.write_access, request)

    def has_object_update_permission(self, request):
        allowed_groups = [AdminGroup.INDEX, AdminGroup.HS]
        is_admin = check_has_access(allowed_groups, request)

        if (
            self.is_own_reservation(request) and "state" not in request.data
        ) or is_admin:
            return True

        if self.state == ReservationStateEnum.CONFIRMED and not is_admin:
            return False

        # If trying to change the state, then check for admin permissions.
        if "state" in request.data:
            if request.data["state"] != self.state:
                return check_has_access(allowed_groups, request)

        return False

    def is_own_reservation(self, request):
        return self.author == request.user
