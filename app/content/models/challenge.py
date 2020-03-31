from django.db import models
from app.util.models import BaseModel, OptionalImage
import uuid


class Challenge(BaseModel):
    id = models.UUIDField(auto_created=True, primary_key=True,
                          default=uuid.uuid4, serialize=False, verbose_name='ID')
    title = models.CharField(max_length=200)
    year = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = 'Challenges'

    def __str__(self):
        return str(self.year) + " - " + self.title
