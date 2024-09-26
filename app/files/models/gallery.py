from django.db import models
from django.db.models import PROTECT

from app.common.permissions import BasePermissionModel
from app.content.models.user import User
from app.util.models import BaseModel


class Gallery(BaseModel, BasePermissionModel):
    read_access = []
    write_access = []

    author = models.OneToOneField(User, on_delete=PROTECT, related_name="galleries")

    class Meta:
        pass

    def __str__(self):
        return self.author
