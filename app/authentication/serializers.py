from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

class RefreshTokenBlacklistSerializer(serializers.Serializer):
    """Blacklists a RefreshToken"""
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])
        refresh.blacklist()
        return refresh
