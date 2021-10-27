from django.db import models
from django.utils.text import slugify

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.content.models.event import Event
from app.util.models import BaseModel, OptionalImage


class Album(BaseModel, BasePermissionModel, OptionalImage):

    title = models.CharField(max_length=100)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=50, primary_key=True)
    write_access = AdminGroup.all()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
