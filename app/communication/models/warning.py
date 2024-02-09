from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel, check_has_access
from app.util.models import BaseModel


class Warning(BaseModel, BasePermissionModel):

    write_access = AdminGroup.admin()
    text = models.CharField(max_length=400, null=True)
    TYPES = (
        (0, "Error"),
        (1, "Warning"),
        (2, "Message"),
    )
    type = models.IntegerField(default=0, choices=TYPES, null=True)

    def __str__(self):
        return f"Warning: {self.type} - Text: {self.text}"

    @classmethod
    def has_write_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_read_permission(cls, request):
        return check_has_access(cls.read_access, request)

    @classmethod
    def has_update_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_delete_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_retrieve_permission(cls, request):
        return check_has_access(cls.read_access, request)
