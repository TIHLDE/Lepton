from rest_framework import serializers

from app.common.serializers import BaseModelSerializer

from ..models import JobPost


class JobPostSerializer(BaseModelSerializer):

    expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = JobPost
        fields = "__all__"  # bad form
