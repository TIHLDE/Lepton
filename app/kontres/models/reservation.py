import uuid

from django.db import models

from app.common.enums import Groups
from app.common.permissions import BasePermissionModel
from app.content.models import User
from app.kontres.enums import ReservationStateEnum
from app.kontres.models.bookable_item import BookableItem
from app.util.models import BaseModel


class Reservation(BaseModel, BasePermissionModel):
    read_access = [Groups.TIHLDE]
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

    def save(self, *args, **kwargs):
        super(Reservation, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.state} - Reservation request by {self.author.first_name} {self.author.last_name} to book {self.bookable_item.name}. Created at {self.created_at}"

    @classmethod
    def has_retrieve_permission(cls, request):
        return request.user and request.user.is_authenticated

    @classmethod
    def has_list_permission(cls, request):
        return cls.has_retrieve_permission(request)

    @classmethod
    def has_write_permission(cls, request):
        return cls.has_reservation_permission(request)

    def has_object_destroy_permission(self, request):
        return (
            self.is_own_reservation(request)
            or self.has_reservation_permission(request)
            or request.user.is_HS_or_Index_member
        )

    @classmethod
    def has_reservation_permission(cls, request):
        # Any authenticated TIHLDE member can create a reservation.
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_TIHLDE_member
        )

    def has_object_update_permission(self, request):
        # Users can update their own reservations, but cannot change the state
        # Admins can update any reservation and change the state
        if not self.is_own_reservation(request):
            return False

        if "state" in request.data and request.data["state"] != self.state:
            # If the user is trying to change the state, check if they are allowed to.
            return request.user and request.user.is_HS_or_Index_member
        return True

    def is_own_reservation(self, request):
        return self.author == request.user
