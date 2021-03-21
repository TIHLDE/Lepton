from django.db import models

from app.common.perm import BasePermissionModel
from app.content.models.user import User
from app.util.models import BaseModel


class Notification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=150)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user}"

    @classmethod
    def has_read_permission(cls, request):
        if request.user is None:
            return False
        return True

    def has_object_read_permission(self, request):
        if request.user is None:
            return False
        return self.user == request.user

    @classmethod
    def has_write_permission(cls, request):
        if request.user is None:
            return False
        return request.method == "PUT"

    def has_object_write_permission(self, request):
        if request.user is None:
            return False
        if request.method == "PUT":
            return self.user == request.user
        return False
