from rest_framework import serializers

from ..models import JobPost


class JobPostSerializer(serializers.ModelSerializer):

    expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = JobPost
        fields = "__all__"  # bad form
