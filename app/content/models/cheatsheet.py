import uuid

from django.db import models

from app.common.enums import (
    AdminGroup,
    NativeCheatsheetType as CheatsheetType,
    Groups,
    NativeUserClass as UserClass,
    NativeUserStudy as UserStudy,
)
from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel


class Cheatsheet(BaseModel, BasePermissionModel):
    write_access = AdminGroup.admin()
    read_access = [Groups.TIHLDE]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    creator = models.CharField(max_length=200)
    grade = models.CharField(max_length=50, choices=UserClass.choices, default=UserClass.FIRST)
    study = models.CharField(max_length=50, choices=UserStudy.choices, default=UserStudy.DATAING)
    course = models.CharField(max_length=200)
    type = models.CharField(max_length=50, choices=CheatsheetType.choices, default=CheatsheetType.LINK)
    official = models.BooleanField(default=False)
    url = models.URLField(max_length=600)

    class Meta:
        verbose_name = "Cheatsheet"
        verbose_name_plural = "Cheatsheets"

    def __str__(self):
        return f"{self.title} {self.course}"
