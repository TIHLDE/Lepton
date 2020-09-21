from rest_framework import serializers


class MakeUserSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=200)
