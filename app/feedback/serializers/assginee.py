from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.content.models.user import User
from app.content.serializers.user import UserListSerializer
from app.feedback.models.assignee import Assignee
from app.feedback.models.feedback import Feedback
from app.feedback.serializers import FeedbackListPolymorphicSerializer


class AssigneeSerializer(BaseModelSerializer):
    user_info = UserListSerializer(source="user", read_only=True)
    feedback = FeedbackListPolymorphicSerializer(read_only=True)

    class Meta:
        model = Assignee
        fields = ["assignee_id", "user_info", "feedback", "created_at", "updated_at"]


class AssigneeCreateUpdateDeleteSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", required=False
    )
    feedback_id = serializers.PrimaryKeyRelatedField(
        queryset=Feedback.objects.all(), source="feedback", required=False
    )

    class Meta:
        model = Assignee
        fields = ["user_id", "feedback_id"]
