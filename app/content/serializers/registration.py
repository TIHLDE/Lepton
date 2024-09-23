from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.content.models.registration import Registration
from app.content.serializers.user import (
    DefaultUserSerializer,
    UserListSerializer,
)
from app.content.util.registration_utils import get_payment_expiredate
from app.forms.enums import NativeEventFormType as EventFormType
from app.forms.serializers.submission import SubmissionInRegistrationSerializer
from app.payment.enums import OrderStatus
from app.payment.util.order_utils import has_paid_order
from app.payment.util.payment_utils import get_payment_order_status


class RegistrationSerializer(BaseModelSerializer):
    user_info = UserListSerializer(source="user", read_only=True)
    survey_submission = serializers.SerializerMethodField()
    has_unanswered_evaluation = serializers.SerializerMethodField()
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
            "payment_expiredate",
            "has_paid_order",
            "wait_queue_number",
            "created_by_admin",
        )

    def get_survey_submission(self, obj):
        submissions = obj.get_submissions(type=EventFormType.SURVEY).first()
        return SubmissionInRegistrationSerializer(submissions).data

    def get_has_unanswered_evaluation(self, obj):
        return obj.user.has_unanswered_evaluations_for(obj.event)

    def get_has_paid_order(self, obj):
        orders = obj.event.orders.filter(user=obj.user)

        if orders and (order := orders.first()).status == OrderStatus.INITIATE:
            order_status = get_payment_order_status(order.order_id)
            order.status = order_status
            order.save()

        return has_paid_order(orders)

    def create(self, validated_data):
        event = validated_data["event"]

        if event.is_paid_event and not event.is_full:
            validated_data["payment_expiredate"] = get_payment_expiredate(event)

        return super().create(validated_data)

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
