from django.db import models

from app.util.models import BaseModel, OptionalImage


class News(BaseModel, OptionalImage):
    title = models.CharField(max_length=200)
    header = models.CharField(max_length=200)
    body = models.TextField()

    class Meta:
        verbose_name_plural = "News"

    def __str__(self):
        return f"{self.title} - {self.header} ({len(self.body)} characters)"
