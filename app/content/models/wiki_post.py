import uuid

from django.db import models
from django.utils.text import slugify

from app.util.models import BaseModel, OptionalImage


class WikiPost(BaseModel, OptionalImage):
    wikipost_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=50, unique=True, null=True)
    description = models.CharField(max_length=200)
    content = models.TextField()

    class Meta:
        verbose_name = "Wiki Post"
        verbose_name_plural = "Wiki Posts"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.wikipost_id} {self.title}"
