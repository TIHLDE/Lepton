from app.common.enums import AdminGroup, Groups
from django.db import models

from app.content.models import Badge, User
from app.util.models import BaseModel
from app.common.perm import BasePermissionModel


class UserBadge(BaseModel, BasePermissionModel):
    write_access = [AdminGroup.INDEX]
    read_access = [AdminGroup.INDEX]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "User badge"
        verbose_name_plural = "User badges"

    def __str__(self):
        return f"{self.badge.title} - {self.user.user_id}"

    @classmethod
    def has_create_permission(cls, request):
        cls.write_access = [Groups.TIHLDE]
        return super().has_write_permission(request)
