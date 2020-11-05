from rest_framework import serializers

from app.util import EnumUtils

from ..models import Event, Priority, Registration, User
from .priority import PrioritySerializer


class EventSerializer(serializers.ModelSerializer):
    expired = serializers.BooleanField(read_only=True)
    registered_users_list = serializers.SerializerMethodField()
    is_user_registered = serializers.SerializerMethodField()
    registration_priorities = serializers.SerializerMethodField()

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
            "priority",
            "category",
            "expired",
            "limit",
            "closed",
            "registered_users_list",
            "list_count",
            "waiting_list_count",
            "is_user_registered",
            "image",
            "image_alt",
            "start_registration_at",
            "end_registration_at",
            "sign_off_deadline",
            "registration_priorities",
            "evaluate_link",
        )

        extra_kwargs = {
            "evaluate_link": {"write_only": True},
        }

    def get_registered_users_list(self, obj):
        """ Return only some user fields"""
        try:
            return [
                {
                    "user_id": user.user_id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
                for user in obj.registered_users_list.all()
            ]
        except User.DoesNotExist:
            return None

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
        except AttributeError:
            pass

        return limit

    def get_is_user_registered(self, obj):
        """ Check if user loading event is signed up """
        request = self.context.get("request")
        if request and hasattr(request, "id"):
            user_id = request.id
            return Registration.objects.filter(
                event__pk=obj.pk, user__user_id=user_id
            ).exists()

        return None

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


class EventCreateAndUpdateSerializer(serializers.ModelSerializer):
    registration_priorities = PrioritySerializer(many=True, required=False)

    class Meta:
        model = Event
        fields = (
            "title",
            "start_date",
            "end_date",
            "location",
            "description",
            "sign_up",
            "priority",
            "category",
            "expired",
            "limit",
            "closed",
            "image",
            "image_alt",
            "start_registration_at",
            "end_registration_at",
            "sign_off_deadline",
            "registration_priorities",
            "evaluate_link",
        )

    def create(self, validated_data):
        registration_priorities_data = validated_data.pop("registration_priorities")
        print(validated_data)
        event = Event.objects.create(**validated_data)
        self.set_registration_priorities(event, registration_priorities_data)

        return event

    def update(self, instance, validated_data):
        if "registration_priorities" in validated_data:
            registration_priorities_data = validated_data.pop("registration_priorities")
            self.set_registration_priorities(instance, registration_priorities_data)
        return super().update(instance, validated_data)

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


class EventAdminSerializer(EventSerializer):
    class Meta:
        model = Event
        fields = EventSerializer.Meta.fields + ("evaluate_link",)


class EventInUserSerializer(EventSerializer):
    expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "start_date",
            "end_date",
            "location",
            "priority",
            "limit",
            "closed",
            "description",
            "expired",
            "image",
            "image_alt",
        ]
