from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.content.models.registration import Registration
from app.content.serializers.user import (
    DefaultUserSerializer,
    UserListSerializer,
)
from app.forms.enums import EventFormType
from app.forms.serializers.submission import SubmissionInRegistrationSerializer
from app.payment.enums import OrderStatus
from app.payment.serializers.order import OrderSerializer


class RegistrationSerializer(BaseModelSerializer):
    user_info = UserListSerializer(source="user", read_only=True)
    survey_submission = serializers.SerializerMethodField()
    has_unanswered_evaluation = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField(required=False)
    has_paid_order = serializers.SerializerMethodField(required=False)
    wait_queue_number = serializers.SerializerMethodField(required=False)

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
            "order",
            "has_paid_order",
            "wait_queue_number",
        )

    def get_survey_submission(self, obj):
        submissions = obj.get_submissions(type=EventFormType.SURVEY).first()
        return SubmissionInRegistrationSerializer(submissions).data

    def get_has_unanswered_evaluation(self, obj):
        return obj.user.has_unanswered_evaluations_for(obj.event)

    def get_order(self, obj):
        order = obj.event.orders.filter(user=obj.user).first()
        if order:
            return OrderSerializer(order).data
        return None

    def get_has_paid_order(self, obj):
        for order in obj.event.orders.filter(user=obj.user):
            if (
                order.status == OrderStatus.CAPTURE
                or order.status == OrderStatus.RESERVE
                or order.status == OrderStatus.SALE
            ):
                return True

    def get_wait_queue_number(self, obj):
        if obj.is_on_wait:
            return obj.wait_queue_number
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
