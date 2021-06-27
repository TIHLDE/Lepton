import uuid

from django.db import models

from app.util.models import BaseModel, OptionalImage


class Event(BaseModel, OptionalImage):
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, serialize=False,
    )
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self):
        return f"{self.title}"
