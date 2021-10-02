from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.content.models.registration import Registration
from app.content.serializers.strike import RegistrationStrikeSerializer
from app.content.serializers.user import UserListSerializer
from app.forms.enums import EventFormType
from app.forms.serializers.submission import SubmissionInRegistrationSerializer


class RegistrationSerializer(BaseModelSerializer):
    user_info = UserListSerializer(source="user", read_only=True)
    survey_submission = serializers.SerializerMethodField()
    waiting_number = serializers.SerializerMethodField()
    has_unanswered_evaluation = serializers.SerializerMethodField()
    strikes = serializers.SerializerMethodField()

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
            "has_unanswered_evaluation",
            "strikes",
        ]

    def get_survey_submission(self, obj):
        submissions = obj.get_submissions(type=EventFormType.SURVEY).first()
        return SubmissionInRegistrationSerializer(submissions).data

    def get_waiting_number(self, obj):
        return obj.get_waiting_number()

    def get_has_unanswered_evaluation(self, obj):
        return obj.user.has_unanswered_evaluations_for(obj.event)

    def get_strikes(self, obj):
        strikes = obj.event.strikes.filter(user = obj.user)
        return RegistrationStrikeSerializer(instance=strikes, many=True).data
