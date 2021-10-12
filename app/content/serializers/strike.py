from rest_framework import serializers

from app.content.models import Strike
from app.content.serializers.event import EventListSerializer
from app.content.serializers.user import DefaultUserSerializer


class BaseStrikeSerializer(serializers.ModelSerializer):
    expires_at = serializers.ReadOnlyField()

    class Meta:
        model = Strike
        fields = ("id", "description", "strike_size", "expires_at", "created_at")


class StrikeSerializer(BaseStrikeSerializer):
    creator = DefaultUserSerializer(read_only=True)
    event = EventListSerializer(read_only=True)
    user = DefaultUserSerializer(read_only=True)

    class Meta:
        model = Strike
        fields = BaseStrikeSerializer.Meta.fields + ("user", "creator", "event")


class UserInfoStrikeSerializer(BaseStrikeSerializer):
    creator = DefaultUserSerializer(read_only=True)
    event = EventListSerializer(read_only=True)

    class Meta:
        model = Strike
        fields = BaseStrikeSerializer.Meta.fields + ("creator", "event")
