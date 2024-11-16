from rest_framework import serializers


class OAuthClientIdSerializer(serializers.Serializer):
    client_id = serializers.CharField(max_length=200)


class OAuthNewCodeSerializer(serializers.Serializer):
    client_id = serializers.CharField(max_length=200)
    redirect_uri = serializers.URLField()


class OAuthAccessTokenSerializer(serializers.Serializer):
    client_id = serializers.CharField(max_length=200)
    client_secret = serializers.CharField(max_length=200)
    code = serializers.CharField(max_length=200)
