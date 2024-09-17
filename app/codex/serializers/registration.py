from app.codex.models.registration import CourseRegistration
from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import UserListSerializer


class RegistrationListSerializer(BaseModelSerializer):
    user = UserListSerializer()

    class Meta:
        model = CourseRegistration
        fields = ("user", "order", "course")


class RegistrationCreateSerializer(BaseModelSerializer):
    class Meta:
        model = CourseRegistration
        fields = ("course",)

    def create(self, validated_data):
        last_order = (
            CourseRegistration.objects.filter(course=validated_data["course"]).count()
            - 1
        )
        validated_data["order"] = last_order + 1

        return CourseRegistration.objects.create(**validated_data)
