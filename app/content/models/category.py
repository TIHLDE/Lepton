from django.db import models

from app.common.enums import AdminGroup, Groups
from app.common.permissions import BasePermissionModel, check_has_access
from app.util.models import BaseModel


class Category(BaseModel, BasePermissionModel):
    write_access = AdminGroup.all()
    read_access = (Groups.TIHLDE,)
    text = models.CharField(max_length=200, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.text}"

    @classmethod
    def has_read_permission(cls, request):
        return check_has_access(cls.read_access, request)

    @classmethod
    def has_retrieve_permission(cls, request):
        return check_has_access(cls.read_access, request)

    @classmethod
    def has_write_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_create_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_update_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_destroy_permission(cls, request):
        return check_has_access(cls.write_access, request)
