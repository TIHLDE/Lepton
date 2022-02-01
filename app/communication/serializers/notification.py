from app.common.serializers import BaseModelSerializer
from app.communication.models import Notification


class NotificationSerializer(BaseModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "description", "link", "read", "created_at"]


class UpdateNotificationSerializer(BaseModelSerializer):
    class Meta:
        model = Notification
        fields = ["read"]

    def update(self, instance, validated_data):
        is_read = validated_data.get("read", instance.read)

        return super().update(instance, dict(read=is_read))
