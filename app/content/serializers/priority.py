from rest_framework import serializers

from app.common.serializers import BaseModelSerializer

from ..models import Priority


class PrioritySerializer(BaseModelSerializer):
    user_class = serializers.IntegerField()
    user_study = serializers.IntegerField()

    class Meta:
        model = Priority
        fields = ["user_class", "user_study"]
