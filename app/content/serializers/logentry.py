from django.contrib.admin.models import LogEntry
from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.content.serializers.content_type import ContentTypeSerializer
from app.content.serializers.user import SimpleUserSerializer


class LogEntryListSerializer(BaseModelSerializer):
    user = SimpleUserSerializer(many=False)
    content_type = ContentTypeSerializer(many=False)
    action_flag = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = (
            "action_time",
            "user",
            "content_type",
            "object_id",
            "object_repr",
            "action_flag",
        )

    def get_action_flag(self, obj):
        if obj.is_addition():
            return "ADDITION"
        if obj.is_change():
            return "CHANGE"
        if obj.is_deletion():
            return "DELETION"
