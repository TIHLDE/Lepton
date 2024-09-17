from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import UserListSerializer
from app.codex.models.registration import CourseRegistration


class RegistrationListSerializer(BaseModelSerializer):
    user = UserListSerializer()

    class Meta:
        model = CourseRegistration
        fields = (
            "user",
            "order"
        )