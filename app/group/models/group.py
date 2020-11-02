from django.contrib.auth.models import Permission
from django.db import models

from enumchoicefield import EnumChoiceField

from app.common.enums import GroupType
from app.util.models import BaseModel, OptionalImage


class Group(OptionalImage, BaseModel):
    """Model for Custom Groups"""

    name = models.CharField(max_length=50)
    permissions = models.ManyToManyField(
        Permission, related_name="groups_permissions", blank=True
    )
    slug = models.SlugField(max_length=50, primary_key=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    contact_email = models.EmailField(max_length=200, null=True, blank=True)
    type = EnumChoiceField(GroupType, default=GroupType.OTHER)

    class meta:
        verbose_name_plural = "Groups"

    def __str__(self):
        return f"{self.name}"
