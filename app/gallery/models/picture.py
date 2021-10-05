import uuid

from django.db import models
from django.db.models.fields.related import ForeignKey
from django.utils.text import slugify

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.content.models.event import Event
from app.util.models import BaseModel


class Picture(BaseModel, BasePermissionModel):

    slug = models.SlugField(default=uuid.uuid4)
    picture = models.URLField(max_length=300)
    event = ForeignKey(Event, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    picture_alt = models.CharField(max_length=100, blank=True)
    write_access = AdminGroup.all()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)

        antall_kopier = 2
        while len(Picture.objects.all().filter(slug=self.slug)) > 0:

            self.slug = self.slug[:-2] if antall_kopier > 2 else self.slug
            self.slug += "-" + str(antall_kopier)

            antall_kopier += 1

        super().save(*args, **kwargs)
