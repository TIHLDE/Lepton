from rest_framework import serializers

from app.blitzed.models.session import Session
from app.common.serializers import BaseModelSerializer


class SessionSerializer(BaseModelSerializer):
    class Meta:
        model = Session
        fields = (
            "id",
            "creator",
            "users",
            "start_time",
            "end_time",
        )

    def validate_start_time(self, value):
        end_time = self.initial_data.get("end_time")
        start_time = value

        if start_time >= end_time:
            raise serializers.ValidationError("Start time must be before end time.")

        return value
