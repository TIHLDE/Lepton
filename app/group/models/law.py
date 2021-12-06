import uuid

from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel, check_has_access
from app.group.models.group import Group
from app.util.models import BaseModel


class Law(BaseModel, BasePermissionModel):
    access = AdminGroup.admin()
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, serialize=False,
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="laws")
    description = models.TextField(default="", blank=True)
    paragraph = models.CharField(default="", blank=True, max_length=100)
    amount = models.IntegerField(default=1)

    class Meta:
        verbose_name_plural = "Laws"
        ordering = ("paragraph",)

    def __str__(self):
        return f"{self.group.name} §{self.paragraph} - {self.description} - {self.amount} enhet"

    @classmethod
    def has_read_permission(cls, request):
        if not Group.check_context(request):
            return check_has_access(cls.access, request)
        return (
            check_has_access(cls.access, request)
            or Group.check_request_user_is_leader(request)
            or Group.check_user_is_fine_master(request)
        )

    @classmethod
    def has_write_permission(cls, request):
        return cls.has_read_permission(request)

    def has_object_write_permission(self, request):
        return self.has_write_permission(request)
