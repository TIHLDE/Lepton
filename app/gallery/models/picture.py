import uuid

from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel

from app.gallery.models.album import Album


class Picture(BaseModel, BasePermissionModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.URLField(max_length=400)
    title = models.CharField(max_length=100, blank=True)
    image_alt = models.CharField(max_length=100, blank=True)
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    write_access = AdminGroup.all()

    def __str__(self):
        return self.image
