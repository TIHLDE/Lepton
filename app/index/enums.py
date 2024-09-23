from django.db import models


class Status(models.TextChoices):
    OPEN = "OPEN", "Åpen"
    CLOSED = "CLOSED", "Lukket"
    IN_PROGRESS = "IN_PROGRESS", "Under arbeid"
    REJECTED = "REJECTED", "Avvist"
