import uuid

from django.db import models

from enumchoicefield import EnumChoiceField

from app.common.enums import (
    AdminGroup,
    CheatsheetType,
    Groups,
    UserClass,
    UserStudy,
)
from app.common.permissions import BasePermissionModel, check_has_access
from app.util.models import BaseModel


class Cheatsheet(BaseModel, BasePermissionModel):
    write_access = AdminGroup.admin()
    read_access = [Groups.TIHLDE]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    creator = models.CharField(max_length=200)
    grade = EnumChoiceField(UserClass, default=UserClass.FIRST)
    study = EnumChoiceField(UserStudy, default=UserStudy.DATAING)
    course = models.CharField(max_length=200)
    type = EnumChoiceField(CheatsheetType, default=CheatsheetType.LINK)
    official = models.BooleanField(default=False)
    url = models.URLField(max_length=600)

    class Meta:
        verbose_name = "Cheatsheet"
        verbose_name_plural = "Cheatsheets"

    def __str__(self):
        return f"{self.title} {self.course}"

    @classmethod
    def has_read_permission(cls, request):
        return check_has_access(cls.read_access, request)

    @classmethod
    def has_retrieve_permission(cls, request):
        return check_has_access(cls.read_access, request)

    @classmethod
    def has_create_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_update_permission(cls, request):
        return check_has_access(cls.write_access, request)

    @classmethod
    def has_destroy_permission(cls, request):
        return check_has_access(cls.write_access, request)
