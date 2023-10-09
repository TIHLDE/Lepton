from django.db import models
import uuid


class BookableItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
