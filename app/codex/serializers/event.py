from rest_framework import serializers

from dry_rest_permissions.generics import DRYPermissionsField

from app.codex.models.event import CodexEvent
from app.codex.util import validate_event_dates
from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import UserListSerializer
from app.group.serializers.group import SimpleGroupSerializer


class CodexEventSerializer(BaseModelSerializer):
    lecturer = UserListSerializer()
    organizer = SimpleGroupSerializer()
    permissions = DRYPermissionsField(
        actions=[
            "write",
            "update",
            "destroy",
        ],
        object_only=True,
    )
    viewer_is_registered = serializers.SerializerMethodField()

    class Meta:
        model = CodexEvent
        fields = (
            "id",
            "title",
            "description",
            "start_date",
            "start_registration_at",
            "end_registration_at",
            "location",
            "mazemap_link",
            "organizer",
            "lecturer",
            "tag",
            "permissions",
            "viewer_is_registered",
        )

    def get_viewer_is_registered(self, obj):
        request = self.context.get("request")
        return obj.registrations.filter(user_id=request.user.user_id).exists()


class CodexEventListSerializer(BaseModelSerializer):
    number_of_registrations = serializers.SerializerMethodField()
    lecturer = UserListSerializer()
    organizer = SimpleGroupSerializer()

    class Meta:
        model = CodexEvent
        fields = (
            "id",
            "title",
            "start_date",
            "location",
            "organizer",
            "lecturer",
            "number_of_registrations",
            "tag",
        )

    def get_number_of_registrations(self, obj):
        return obj.registrations.count()


class CodexEventCreateSerializer(BaseModelSerializer):
    class Meta:
        model = CodexEvent
        fields = (
            "title",
            "description",
            "start_date",
            "start_registration_at",
            "end_registration_at",
            "tag",
            "location",
            "mazemap_link",
            "organizer",
            "lecturer",
        )

    def create(self, validated_data):
        validate_event_dates(validated_data)
        return super().create(validated_data)


class CodexEventUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = CodexEvent
        fields = (
            "title",
            "description",
            "start_date",
            "start_registration_at",
            "end_registration_at",
            "tag",
            "location",
            "mazemap_link",
            "organizer",
            "lecturer",
        )

    def update(self, instance, validated_data):
        validate_event_dates(validated_data)
        return super().update(instance, validated_data)
