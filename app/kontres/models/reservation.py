import uuid

from django.core.exceptions import ValidationError
from django.db import models

from app.content.models import User
from app.kontres.enums import ReservationStateEnum
from app.kontres.models.bookable_item import BookableItem
from app.util.models import BaseModel


class Reservation(BaseModel):
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

    def clean(self):
        # Check if end_time is greater than start_time
        if self.end_time <= self.start_time:
            raise ValidationError("end_time must be after start_time")

        # Check if start_time and end_time are provided
        if not self.start_time or not self.end_time:
            raise ValidationError("Both start_time and end_time must be provided")

    def save(self, *args, **kwargs):
        self.clean()
        super(Reservation, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.state} - Reservation request by {self.author.first_name} {self.author.last_name} to book {self.bookable_item.name}. Created at {self.created_at}"
