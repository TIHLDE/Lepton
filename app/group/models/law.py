import uuid

from django.db import models

from app.common.enums import AdminGroup, Groups
from app.common.permissions import BasePermissionModel, check_has_access
from app.group.models.group import Group
from app.util.models import BaseModel


class Law(BaseModel, BasePermissionModel):
    read_access = [Groups.TIHLDE]
    write_access = AdminGroup.admin()
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, serialize=False,
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="laws")
    description = models.TextField(default="", blank=True)
    paragraph = models.CharField(default="", blank=True, max_length=10)
    amount = models.IntegerField(default=1)

    class meta:
        verbose_name_plural = "Laws"
        ordering = ("paragraph",)

    def __str__(self):
        return f"§ {self.paragraph} - {self.description} - {self.amount} enhet"

    @classmethod
    def has_read_permission(cls, request):
        return request.user and (
            check_has_access(cls.read_access, request)
            or request.user.is_member_of(
                Group.get_group_from_permission_context(request)
            )
        )

    @classmethod
    def has_write_permission(cls, request):
        return check_has_access(
            cls.write_access, request
        ) or Group.check_request_user_is_leader(request)

    def has_object_write_permission(self, request):
        return self.has_write_permission(request)
