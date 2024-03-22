from django.db import models

from app.common.enums import Groups
from app.common.permissions import BasePermissionModel, check_has_access
from app.content.models.user import User
from app.util.models import BaseModel


class Notification(BaseModel, BasePermissionModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=150)
    description = models.TextField(default="", blank=True)
    link = models.CharField(max_length=150, blank=True, null=True)
    read = models.BooleanField(default=False)

    read_access = (Groups.TIHLDE,)
    write_access = (Groups.TIHLDE,)

    def __str__(self):
        return f"Notification for {self.user}, title: {self.title}, description: {self.description}"

    @classmethod
    def has_write_permission(cls, request):
        if request.method == "POST":
            return False
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_read_permission(cls, request):
        return check_has_access(cls.read_access, request)

    @classmethod
    def has_retrieve_permission(cls, request):
        return check_has_access(cls.read_access, request)

    @classmethod
    def has_update_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_destroy_permission(cls, request):
        return False

    def has_object_read_permission(self, request):
        return self.user == request.user

    def has_object_retrieve_permission(self, request):
        return self.user == request.user

    def has_object_update_permission(self, request):
        return self.user == request.user
