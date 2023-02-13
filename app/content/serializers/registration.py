from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.content.models.registration import Registration
from app.content.serializers.user import (
    DefaultUserSerializer,
    UserListSerializer,
)
from app.forms.enums import EventFormType
from app.forms.serializers.submission import SubmissionInRegistrationSerializer


class RegistrationSerializer(BaseModelSerializer):
    user_info = UserListSerializer(source="user", read_only=True)
    survey_submission = serializers.SerializerMethodField()
    has_unanswered_evaluation = serializers.SerializerMethodField()
    payment_link = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Registration
        fields = (
            "registration_id",
            "user_info",
            "is_on_wait",
            "has_attended",
            "allow_photo",
            "created_at",
            "survey_submission",
            "has_unanswered_evaluation",
            "payment_link",
        )

    def get_survey_submission(self, obj):
        submissions = obj.get_submissions(type=EventFormType.SURVEY).first()
        return SubmissionInRegistrationSerializer(submissions).data

    def get_has_unanswered_evaluation(self, obj):
        return obj.user.has_unanswered_evaluations_for(obj.event)

    def get_payment_link(self, obj):
        if obj.event.is_paid_event:
            return obj.event.orders.filter(user=obj.user).first().payment_link
        return None


class PublicRegistrationSerializer(BaseModelSerializer):
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = Registration
        fields = ("user_info",)

    def get_user_info(self, obj):
        user = obj.user
        if user.public_event_registrations:
            return DefaultUserSerializer(user).data
        return None
