from django.db import models

from app.common.enums import Groups
from app.common.permissions import BasePermissionModel
from app.content.models.user import User
from app.util.models import BaseModel


class Session(BaseModel, BasePermissionModel):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    users = models.ManyToManyField(User, related_name="sessions", blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session {self.session_id}"

    class Meta:
        verbose_name_plural = "Sessions"
