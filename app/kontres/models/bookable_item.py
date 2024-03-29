import uuid

from django.db import models

from app.common.enums import AdminGroup, Groups
from app.common.permissions import BasePermissionModel, check_has_access
from app.util.models import BaseModel, OptionalImage


class BookableItem(BaseModel, BasePermissionModel, OptionalImage):
    write_access = AdminGroup.admin()
    read_access = [Groups.TIHLDE]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    allows_alcohol = models.BooleanField(default=False)

    @classmethod
    def has_read_permission(cls, request):
        return check_has_access(cls.read_access, request)

    @classmethod
    def has_retrieve_permission(cls, request):
        return check_has_access(cls.read_access, request)

    @classmethod
    def has_destroy_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_create_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_update_permission(cls, request):
        return check_has_access(cls.write_access, request)

    def has_object_destroy_permission(self, request):
        return self.check_has_admin_permission(request)

    def has_object_update_permission(self, request):
        return self.check_has_admin_permission(request)

    def check_has_admin_permission(self, request):
        return check_has_access([AdminGroup.INDEX, AdminGroup.HS], request)

    def __str__(self):
        return self.name
