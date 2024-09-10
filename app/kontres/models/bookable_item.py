import uuid
from django.db import models

from app.common.enums import Groups
from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel, OptionalImage
from app.group.models import Group

class BookableItem(BaseModel, BasePermissionModel, OptionalImage):
    read_access = ( Groups.TIHLDE, )
    write_access = ( Groups.TIHLDE, )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    allows_alcohol = models.BooleanField(default=False)
    owner_group = models.ForeignKey(
       Group,
       on_delete=models.SET_NULL,
       null=True,
       related_name="owner_group"   
    )

    @classmethod
    def has_update_permission(cls, request):
        return cls.has_write_permission(request)
    
    @classmethod
    def has_delete_permission(cls, request):
        return cls.has_delete_permission(request)
    
    def has_object_update_permission(self):
        return self.user.is_leader_of(self.owner_group)
    
    def has_object_delete_permission(self):
        return self.user.is_leader_of(self.owner_group)