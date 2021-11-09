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
from app.common.permissions import BasePermissionModel
from app.util.models import TimeStampedModel


class Cheatsheet(TimeStampedModel, BasePermissionModel):
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
