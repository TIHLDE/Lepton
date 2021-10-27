from django.db import models
from django.utils.text import slugify

from enumchoicefield import EnumChoiceField

from app.common.enums import AdminGroup, GroupType
from app.common.permissions import BasePermissionModel, set_user_id
from app.util.models import BaseModel, OptionalImage


class Group(OptionalImage, BaseModel, BasePermissionModel):
    """Model for Custom Groups"""

    write_access = AdminGroup.admin()
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, primary_key=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    contact_email = models.EmailField(max_length=200, null=True, blank=True)
    type = EnumChoiceField(GroupType, default=GroupType.OTHER)

    class meta:
        verbose_name_plural = "Groups"

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if self.slug == "":
            self.slug = slugify(self.name)
        else:
            self.slug = slugify(self.slug)
        super().save(*args, **kwargs)

    @classmethod
    def check_request_user_is_leader(cls, request):
        if request.id is None:
            set_user_id(request)
        group_slug = request.parser_context["kwargs"]["slug"]
        group = cls.objects.get(slug=group_slug)
        return group.memberships.get(
            group__slug=group_slug, user__user_id=request.id
        ).is_leader()

    @classmethod
    def has_write_permission(cls, request):
        from app.group.models import Membership

        try:
            return cls.check_request_user_is_leader(
                request
            ) or super().has_write_permission(request)
        except (Membership.DoesNotExist, KeyError, AssertionError):
            return super().has_write_permission(request)

    def has_object_write_permission(self, request):
        from app.group.models import Membership

        if request.id is None:
            set_user_id(request)
        try:
            return self.memberships.get(
                group__slug=self.slug, user__user_id=request.id
            ).is_leader() or super().has_object_write_permission(request)
        except Membership.DoesNotExist:
            return super().has_object_write_permission(request)
