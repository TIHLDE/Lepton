from rest_framework import serializers
from ..models import Priority


class PrioritySerializer(serializers.ModelSerializer):
    user_class = serializers.IntegerField()
    user_study = serializers.IntegerField()

    class Meta:
        model = Priority
        fields = ['user_class', 'user_study']
