from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.content.models.registration import Registration
from app.content.serializers.user import UserListSerializer
from app.forms.enums import EventFormType
from app.forms.serializers.submission import SubmissionInRegistrationSerializer


class RegistrationSerializer(BaseModelSerializer):
    user_info = UserListSerializer(source="user")
    survey_submission = serializers.SerializerMethodField()
    waiting_number = serializers.SerializerMethodField()

    class Meta:
        model = Registration
        fields = [
            "registration_id",
            "user_info",
            "is_on_wait",
            "has_attended",
            "allow_photo",
            "created_at",
            "survey_submission",
            "waiting_number",
        ]

    # def get_user_info(self, obj):
    #     return obj.user

    def get_survey_submission(self, obj):
        submissions = obj.get_submissions(type=EventFormType.SURVEY).first()
        return SubmissionInRegistrationSerializer(submissions).data

    def get_waiting_number(self, obj):
        return obj.get_waiting_number()
