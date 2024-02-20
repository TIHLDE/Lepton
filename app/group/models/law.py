import uuid

from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel, check_has_access
from app.group.models.group import Group
from app.util.models import BaseModel


class Law(BaseModel, BasePermissionModel):
    write_access = AdminGroup.admin()
    read_access = AdminGroup.admin()

    id = models.UUIDField(
        auto_created=True,
        primary_key=True,
        default=uuid.uuid4,
        serialize=False,
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="laws")
    description = models.TextField(default="", blank=True)
    paragraph = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    title = models.CharField(max_length=100)
    amount = models.IntegerField(default=1)

    class Meta:
        verbose_name_plural = "Laws"
        ordering = ("paragraph",)

    def __str__(self):
        return f"{self.group.name} §{self.paragraph} {self.title} - {self.description} - {self.amount} enhet"

    @classmethod
    def has_create_permission(cls, request):
        return cls.check_has_write_permission(cls, request)

    @classmethod
    def has_destroy_permission(cls, request):
        return cls.check_has_write_permission(cls, request)

    @classmethod
    def has_update_permission(cls, request):
        return cls.check_has_write_permission(cls, request)

    @classmethod
    def has_list_permission(cls, request):
        return cls.check_has_read_permission(cls, request)

    @classmethod
    def has_retrieve_permission(cls, request):
        return cls.check_has_read_permission(cls, request)

    def has_object_destroy_permission(self, request):
        return True

    def has_object_update_permission(self, request):
        return True

    def has_object_retrieve_permission(self, request):
        return True

    def check_has_read_permission(self, request):
        if not Group.check_context(request):
            return check_has_access(self.read_access, request)
        return (
            check_has_access(self.read_access, request)
            or request.user
            and request.user.is_member_of(
                Group.get_group_from_permission_context(request)
            )
        )

    def check_has_write_permission(self, request):
        if not Group.check_context(request):
            return check_has_access(self.write_access, request)
        return request.user and (
            Group.check_user_is_fine_master(request)
            or check_has_access(self.write_access, request)
            or Group.check_request_user_is_leader(request)
        )
