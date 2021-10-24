from rest_framework import serializers

from dry_rest_permissions.generics import DRYPermissionsField
from sentry_sdk import capture_exception

from app.common.serializers import BaseModelSerializer
from app.content.models import Event, Priority
from app.content.serializers.priority import PrioritySerializer
from app.group.serializers.group import GroupSerializer
from app.util import EnumUtils


class EventSerializer(serializers.ModelSerializer):
    expired = serializers.BooleanField(read_only=True)
    registration_priorities = serializers.SerializerMethodField()
    evaluation = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    survey = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    group = GroupSerializer(read_only=True)
    permissions = DRYPermissionsField(actions=["write", "read"], object_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "start_date",
            "end_date",
            "location",
            "description",
            "sign_up",
            "category",
            "expired",
            "limit",
            "closed",
            "list_count",
            "waiting_list_count",
            "group",
            "image",
            "image_alt",
            "start_registration_at",
            "end_registration_at",
            "sign_off_deadline",
            "registration_priorities",
            "evaluation",
            "survey",
            "updated_at",
            "can_cause_strikes",
            "enforces_previous_strikes",
            "permissions",
        )

    def validate_limit(self, limit):
        """
        Validate that the event limit is greater or equal to 0 and
        that the limit can not be lower than the number of registered users.
        If the limit is already 0, then do not let that effect updating other fields
        """
        try:
            if limit < 0:
                raise serializers.ValidationError(
                    "Event limit can not a negative integer"
                )
            elif (
                limit < self.instance.registered_users_list.all().count()
                and self.instance.limit != 0
            ):
                raise serializers.ValidationError(
                    "Event limit can not be lower than number of registered users."
                )
        except AttributeError as attribute_error:
            capture_exception(attribute_error)

        return limit

    def get_registration_priorities(self, obj):
        try:
            return [
                {
                    "user_class": registration_priority.user_class.value,
                    "user_study": registration_priority.user_study.value,
                }
                for registration_priority in obj.registration_priorities.all()
            ]
        except Priority.DoesNotExist:
            return None


class EventListSerializer(serializers.ModelSerializer):
    expired = serializers.BooleanField(read_only=True)
    group = GroupSerializer(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "start_date",
            "end_date",
            "location",
            "expired",
            "group",
            "image",
            "image_alt",
            "updated_at",
        ]


class EventCreateAndUpdateSerializer(BaseModelSerializer):
    registration_priorities = PrioritySerializer(many=True, required=False)

    class Meta:
        model = Event
        fields = (
            "can_cause_strikes",
            "category",
            "closed",
            "description",
            "end_date",
            "end_registration_at",
            "enforces_previous_strikes",
            "expired",
            "group",
            "image",
            "image_alt",
            "limit",
            "location",
            "registration_priorities",
            "sign_off_deadline",
            "sign_up",
            "start_date",
            "start_registration_at",
            "title",
        )

    def create(self, validated_data):
        registration_priorities_data = None
        if "registration_priorities" in validated_data:
            registration_priorities_data = validated_data.pop("registration_priorities")
        event = super().create(validated_data)
        if registration_priorities_data:
            self.set_registration_priorities(event, registration_priorities_data)

        return event

    def update(self, instance, validated_data):
        registration_priorities_data = None
        if "registration_priorities" in validated_data:
            registration_priorities_data = validated_data.pop("registration_priorities")
        event = super().update(instance, validated_data)
        if registration_priorities_data:
            self.set_registration_priorities(event, registration_priorities_data)
        return event

    def set_registration_priorities(self, event, registration_priorities_data):
        event.registration_priorities.clear()
        for registration_priority_data in registration_priorities_data:
            registration_priority_to_add = self.get_registration_priority_from_data(
                registration_priority_data
            )
            event.registration_priorities.add(registration_priority_to_add)

    @staticmethod
    def get_registration_priority_from_data(data):
        user_class, user_study = EnumUtils.get_user_enums(**data)
        registration_priority, created = Priority.objects.get_or_create(
            user_class=user_class, user_study=user_study
        )

        return registration_priority
