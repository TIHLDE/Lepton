from django.db import models
from app.content.models import User
from app.kontres.reservation_state import ReservationStateEnum
from app.kontres.models.bookable_item import BookableItem


class Reservation(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    bookable_item = models.ForeignKey(BookableItem, on_delete=models.CASCADE, related_name='reservations', default=1)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    state = models.CharField(max_length=15, choices=ReservationStateEnum.choices, default=ReservationStateEnum.PENDING)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.state} - Reservation request by {self.author} to book {self.bookable_item.name}"


