from rest_framework import serializers

from dry_rest_permissions.generics import DRYPermissionsField

from app.codex.models.course import Course
from app.codex.serializers.registration import RegistrationListSerializer
from app.codex.util import validate_course_dates
from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import UserListSerializer
from app.group.serializers.group import SimpleGroupSerializer


class CourseSerializer(BaseModelSerializer):
    lecturer = UserListSerializer()
    organizer = SimpleGroupSerializer()
    registrations = RegistrationListSerializer(many=True)
    permissions = DRYPermissionsField(
        actions=[
            "write",
            "update",
            "destroy",
        ],
        object_only=True,
    )

    class Meta:
        model = Course
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
            "registrations",
            "tag",
            "permissions",
        )


class CourseListSerializer(BaseModelSerializer):
    number_of_registrations = serializers.SerializerMethodField()
    lecturer = UserListSerializer()
    organizer = SimpleGroupSerializer()

    class Meta:
        model = Course
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


class CourseCreateSerializer(BaseModelSerializer):
    class Meta:
        model = Course
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
        validate_course_dates(validated_data)
        return super().create(validated_data)


class CourseUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Course
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
        validate_course_dates(validated_data)
        return super().update(instance, validated_data)
