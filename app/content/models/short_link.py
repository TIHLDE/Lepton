from django.db import models
from django.utils.text import slugify

from app.content.models import User
from app.util.models import BaseModel


class ShortLink(BaseModel):
    name = models.CharField(max_length=50, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="short_links")
    url = models.URLField(max_length=600)

    class Meta:
        verbose_name = "Short link"
        verbose_name_plural = "Short links"

    def save(self, *args, **kwargs):
        self.name = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.user.user_id}"
