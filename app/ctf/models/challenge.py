import uuid

from django.db import models

from app.util.models import BaseModel, OptionalImage


class Challenge(BaseModel, OptionalImage):
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, serialize=False,
    )
    custom_flag = models.CharField(max_length=500, blank=True) 
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200, blank=True)

    event = models.ForeignKey("ctf.Event", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Challenge"
        verbose_name_plural = "Challenges"

    def __str__(self):
        return f"{self.title}"
