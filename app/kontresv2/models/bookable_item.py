import uuid
from django.db import models

from app.common.enums import AdminGroup, Groups
from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel, OptionalImage


class BookableItem(BaseModel, BasePermissionModel, OptionalImage):
    write_access = AdminGroup.admin()
    read_access = [Groups.TIHLDE]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    allows_alcohol = models.BooleanField(default=False)
