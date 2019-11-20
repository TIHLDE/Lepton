from rest_framework import serializers

class AuthSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=200)

class MakeSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=200)

