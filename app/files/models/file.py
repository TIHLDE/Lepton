from django.db import models
from django.db.models import PROTECT

from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel
from app.files.models.gallery import Gallery


class File(BaseModel, BasePermissionModel):
    read_access = []
    write_access = []

    title = models.CharField(max_length=80)
    url = models.URLField()
    description = models.TextField(blank=True)
    gallery = models.ForeignKey(Gallery, on_delete=PROTECT, related_name="files", blank=False)

    class Meta:
        pass

    def __str__(self):
        return self.title