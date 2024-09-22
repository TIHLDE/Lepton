from rest_framework import serializers

from app.codex.models.registration import CodexEventRegistration
from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import UserListSerializer


class RegistrationListSerializer(BaseModelSerializer):
    user_info = UserListSerializer(source="user", read_only=True)

    class Meta:
        model = CodexEventRegistration
        fields = ("registration_id", "user_info", "order")


class RegistrationCreateSerializer(BaseModelSerializer):
    class Meta:
        model = CodexEventRegistration
        fields = ("event",)

    def create(self, validated_data):
        last_order = (
            CodexEventRegistration.objects.filter(event=validated_data["event"]).count()
            - 1
        )
        validated_data["order"] = last_order + 1

        return CodexEventRegistration.objects.create(**validated_data)
