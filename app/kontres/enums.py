from django.db import models


class ReservationStateEnum(models.TextChoices):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
