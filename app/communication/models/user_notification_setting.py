from django.db import models

from app.communication.enums import UserNotificationSettingType
from app.communication.exceptions import AllChannelsUnselected
from app.content.models.user import User
from app.util.models import BaseModel


class UserNotificationSetting(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_notification_settings"
    )
    notification_type = models.CharField(
        max_length=30, choices=UserNotificationSettingType.choices
    )

    email = models.BooleanField(default=True)
    website = models.BooleanField(default=True)
    slack = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "notification_type")
        verbose_name = "User notification setting"
        verbose_name_plural = "User notification settings"
        ordering = ("notification_type",)

    def __str__(self):
        return (
            f"UserNotificationSetting for {self.user}, type: {self.notification_type}"
        )

    def clean(self):
        if not self.email and not self.website and not self.slack:
            raise AllChannelsUnselected("Du må velge minst en kommunikasjonsmetode")

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
