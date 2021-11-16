from rest_framework import serializers

from app.career.models.job_post import JobPost
from app.common.serializers import BaseModelSerializer


class JobPostSerializer(BaseModelSerializer):

    expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = JobPost
        fields = "__all__"
