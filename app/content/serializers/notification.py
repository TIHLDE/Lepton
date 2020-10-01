from rest_framework import serializers

from ..models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """ Serilaize all the notifcations """

    class Meta:
        model = Notification
        fields = ["user", "message", "read"]


class UpdateNotificationSerializer(serializers.ModelSerializer):
    """ Serialize notifications for update """

    class Meta:
        model = Notification
        fields = ["read"]

    def update(self, instance, validated_data):
        instance.read = validated_data.get("read", instance.read)
        instance.save()
        return instance
