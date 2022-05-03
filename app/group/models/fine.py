import uuid

from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel, check_has_access
from app.content.models.user import User
from app.group.exceptions import UserIsNotInGroup
from app.group.models.group import Group
from app.util.models import BaseModel, OptionalImage


class Fine(BaseModel, OptionalImage, BasePermissionModel):

    access = AdminGroup.admin()
    id = models.UUIDField(
        auto_created=True,
        primary_key=True,
        default=uuid.uuid4,
        serialize=False,
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fines")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="fines_created"
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="fines")
    amount = models.IntegerField(default=1)
    approved = models.BooleanField(default=False)
    payed = models.BooleanField(default=False)
    description = models.CharField(default="", blank=True, max_length=100)
    reason = models.TextField(default="", blank=True)
    defense = models.TextField(default="", blank=True)

    class Meta:
        verbose_name_plural = "Fines"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.group.name} {self.description} {self.user.user_id} {self.amount}"

    def clean(self):
        if not self.user.is_member_of(self.group):
            raise UserIsNotInGroup(
                f"{self.user.first_name} {self.user.last_name} er ikke medlem i gruppen"
            )

    def save(self, *args, **kwargs):
        self.full_clean()

        return super().save(*args, **kwargs)

    @classmethod
    def has_read_permission(cls, request):
        if not Group.check_context(request):
            return check_has_access(cls.access, request)
        return request.user and (
            check_has_access(cls.access, request)
            or request.user.is_member_of(
                Group.get_group_from_permission_context(request)
            )
        )

    @classmethod
    def has_create_permission(cls, request):
        if not Group.check_context(request):
            return check_has_access(cls.access, request)
        return check_has_access(cls.access, request) or request.user.is_member_of(
            Group.get_group_from_permission_context(request)
        )

    @classmethod
    def has_update_permission(cls, request):
        if not Group.check_context(request):
            return check_has_access(cls.access, request)
        return request.user and (
            Group.check_user_is_fine_master(request)
            or check_has_access(cls.access, request)
            or Group.check_request_user_is_leader(request)
        )

    @classmethod
    def has_destroy_permission(cls, request):
        return cls.has_update_permission(request)

    def has_object_update_permission(self, request):
        return self.has_update_permission(request)

    def has_object_destroy_permission(self, request):
        return self.has_destroy_permission(request)

    def has_object_update_defense_permission(self, request):
        return self.user == request.user
