import uuid

from django.db import models

from app.util.models import BaseModel, OptionalImage


class Badge(BaseModel, OptionalImage):
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, serialize=False,
    )
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "Badges"

    def __str__(self):
        return f"{self.title} - {self.description}"
