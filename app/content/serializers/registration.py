from rest_framework import serializers

from app.common.serializers import BaseModelSerializer

from ..models import Registration, User


class RegistrationSerializer(BaseModelSerializer):
    user_info = serializers.SerializerMethodField()
    submissions = serializers.SerializerMethodField()

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

    def get_submissions(self, obj):
        forms = obj.event.forms.all()
        submissions = forms.submissions.filter(user=obj.user)
        return SubmissionInRegistrationSerializer(submissions, many=True)
