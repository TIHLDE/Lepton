from app.common.serializers import BaseModelSerializer
from app.communication.models import UserNotificationSetting


class UserNotificationSettingSerializer(BaseModelSerializer):
    class Meta:
        model = UserNotificationSetting
        fields = ("type", "email", "website", "slack",)
