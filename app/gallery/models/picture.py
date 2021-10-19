import uuid

from django.db import models
from django.db.models.fields.related import ForeignKey

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.content.models.event import Event
from app.util.models import BaseModel


class Album(BaseModel, BasePermissionModel):

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    event = ForeignKey(Event, on_delete=models.SET_NULL, null=True)
    write_access = AdminGroup.all()

    def __str__(self):
        return self.title


class Picture(BaseModel, BasePermissionModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    picture = models.URLField(max_length=300)
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    picture_alt = models.CharField(max_length=100, blank=True)
    write_access = AdminGroup.all()
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.picture)
