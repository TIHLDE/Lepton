from rest_framework import serializers

from app.badge.models import UserBadge
from app.common.serializers import BaseModelSerializer
from app.content.models import User
from app.content.serializers.user import DefaultUserSerializer


class LeaderboardSerializer(BaseModelSerializer):
    number_of_badges = serializers.IntegerField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "user",
            "number_of_badges",
        )

    def get_user(self, obj):
        return DefaultUserSerializer(obj).data


class LeaderboardForBadgeSerializer(BaseModelSerializer):
    user = DefaultUserSerializer()

    class Meta:
        model = UserBadge
        fields = (
            "user",
            "created_at",
        )
