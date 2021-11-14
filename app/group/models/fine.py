import uuid

from django.db import models

from app.common.permissions import BasePermissionModel
from app.content.models.user import User
from app.group.models.group import Group
from app.util.models import BaseModel


class Fine(BaseModel, BasePermissionModel):
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, serialize=False,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fines")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="fines")
    amount = models.IntegerField(default=1)
    approved = models.BooleanField(default=False)
    payed = models.BooleanField(default=False)
    description = models.TextField(default="", blank=True)
