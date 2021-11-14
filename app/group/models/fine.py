import uuid

from django.db import models
from app.common.enums import AdminGroup

from app.common.permissions import BasePermissionModel
from app.content.models.user import User
from app.group.models.group import Group
from app.util.models import BaseModel


class Fine(BaseModel, BasePermissionModel):
    read_access = AdminGroup.admin()
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, serialize=False,
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fines")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="fines_created", default=None
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="fines")
    amount = models.IntegerField(default=1)
    approved = models.BooleanField(default=False)
    payed = models.BooleanField(default=False)
    description = models.TextField(default="", blank=True)
    

    
    # @classmethod
    # def has_create_permission(cls, request):
        
        
