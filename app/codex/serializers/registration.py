from app.codex.models.registration import CourseRegistration
from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import UserListSerializer


class RegistrationListSerializer(BaseModelSerializer):
    user = UserListSerializer()

    class Meta:
        model = CourseRegistration
        fields = ("user", "order")
