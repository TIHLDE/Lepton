from django.db import models
from django.db.models.fields.related import ForeignKey

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.content.models.event import Event
from app.util.models import BaseModel


class Picture(BaseModel, BasePermissionModel):

    picture = models.URLField()
    event = ForeignKey(Event, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    picture_alt = models.CharField(max_length=100, blank=True)
    write_access = AdminGroup.all()

    def __str__(self):
        return self.title
