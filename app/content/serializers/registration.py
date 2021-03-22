from rest_framework import serializers

from app.common.serializers import BaseModelSerializer

from ..models import Registration, User


class RegistrationSerializer(BaseModelSerializer):
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = Registration
        fields = [
            "registration_id",
            "user_info",
            "is_on_wait",
            "has_attended",
            "allow_photo",
            "created_at",
        ]

    def get_user_info(self, obj):
        """ Gets the necessary info from user """
        user = User.objects.get(user_id=obj.user_id)
        return {
            "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "image": user.image,
            "email": user.email,
            "user_class": user.user_class,
            "user_study": user.user_study,
            "allergy": user.allergy,
        }
