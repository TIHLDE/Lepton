from django.db import models

from app.common.enums import AdminGroup, Groups
from app.common.permissions import BasePermissionModel
from app.badge.models import Badge
from app.util.models import BaseModel


class UserBadge(BaseModel, BasePermissionModel):
    write_access = [AdminGroup.INDEX]
    read_access = [AdminGroup.INDEX]
    user = models.ForeignKey("content.user", on_delete=models.CASCADE, related_name="user_badges")
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
