from django.db import models
from app.communication.enums import UserNotificationSettingType

from app.content.models.user import User
from app.util.models import BaseModel


class UserNotificationSetting(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_notification_settings"
    )
    type = models.CharField(
        max_length=30, choices=UserNotificationSettingType.choices
    )

    email = models.BooleanField(default=True)
    website = models.BooleanField(default=True)
    slack = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "type")
        verbose_name = "User notification setting"
        verbose_name_plural = "User notification settings"
        ordering = ("type",)

    def __str__(self):
        return f"UserNotificationSetting for {self.user}, type: {self.type}"

    @classmethod
    def has_read_permission(cls, request):
        return request.user is not None

    def has_object_read_permission(self, request):
        if request.user is None:
            return False
        return self.user == request.user

    @classmethod
    def has_write_permission(cls, request):
        return request.user is not None

    def has_object_write_permission(self, request):
        if request.user is None:
            return False
        return self.user == request.user
