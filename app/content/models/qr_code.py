from django.db import models

from app.common.enums import Groups
from app.common.permissions import BasePermissionModel, check_has_access
from app.content.models import User
from app.util.models import BaseModel, OptionalImage


class QRCode(BaseModel, OptionalImage, BasePermissionModel):
    write_access = (Groups.TIHLDE,)
    read_access = (Groups.TIHLDE,)

    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="qr_codes")
    content = models.CharField(max_length=600)

    class Meta:
        verbose_name = "qr_code"
        verbose_name_plural = "qr_codes"

    def __str__(self):
        return f"{self.name} - {self.user.user_id}"

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

    def has_object_retrieve_permission(self, request):
        return request.user == self.user

    def has_object_update_permission(self, request):
        return request.user == self.user

    def has_object_destroy_permission(self, request):
        return request.user == self.user
