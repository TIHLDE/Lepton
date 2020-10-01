from django.db import models

from app.util.models import BaseModel


class Category(BaseModel):
    text = models.CharField(max_length=200, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.text}"
