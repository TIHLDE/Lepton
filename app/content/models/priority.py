from django.db import models

from enumchoicefield import EnumChoiceField

from app.common.enums import UserClass, UserStudy
from app.util.models import BaseModel


class Priority(BaseModel):
    priority_id = models.AutoField(primary_key=True)

    user_class = EnumChoiceField(UserClass, default=UserClass.FIRST)
    user_study = EnumChoiceField(UserStudy, default=UserStudy.DATAING)

    class Meta:
        ordering = ("user_class", "user_study")
        verbose_name_plural = "Priorities"

    def __str__(self):
        return f"{self.user_class} {self.user_study}"
