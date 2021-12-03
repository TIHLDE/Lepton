import uuid

from django.core.exceptions import ValidationError
from django.db import models

from app.common.enums import AdminGroup, Groups
from app.common.permissions import BasePermissionModel, check_has_access
from app.content.models.user import User
from app.group.models.group import Group
from app.util.models import BaseModel


class Fine(BaseModel, BasePermissionModel):

    read_access = [Groups.TIHLDE]
    write_access = AdminGroup.admin()
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, serialize=False,
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fines")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="fines_created", default=None
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="fines")
    amount = models.IntegerField(default=1)
    approved = models.BooleanField(default=False)
    payed = models.BooleanField(default=False)
    description = models.TextField(default="", blank=True)
    reason = models.TextField(default="", blank=True)

    def clean(self):
        if not self.user.is_member_of(self.group):
            ValidationError("Brukeren er ikke medlem av denne gruppen")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Fine, self).save(*args, **kwargs)

    @classmethod
    def has_read_permission(cls, request):
        return request.user and (
            check_has_access(cls.read_access, request)
            or request.user.is_member_of(
                Group.get_group_from_permission_context(request)
            )
        )

    @classmethod
    def has_create_permission(cls, request):
        return cls.has_read_permission(request)

    @classmethod
    def has_update_permission(cls, request):

        return request.user and (
            Group.check_user_is_fine_master(request)
            or check_has_access(cls.write_access, request)
            or Group.check_request_user_is_leader(request)
        )

    @classmethod
    def has_destroy_permission(cls, request):
        return cls.has_update_permission(request)

    def has_object_update_permission(self, request):
        return self.has_update_permission(request)

    def has_object_destroy_permission(self, request):
        return self.has_destroy_permission(request)
