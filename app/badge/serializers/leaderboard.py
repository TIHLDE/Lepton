from rest_framework import serializers

from app.badge.models import UserBadge
from app.common.serializers import BaseModelSerializer
from app.content.models import User
from app.content.serializers.user import DefaultUserSerializer


class LeaderboardSerializer(BaseModelSerializer):
    number_of_badges = serializers.SerializerMethodField()
    user = DefaultUserSerializer()

    class Meta:
        model = User
        fields = (
            "user",
            "number_of_badges",
        )

    def get_number_of_badges(self, obj):
        return obj.user_badges.count()


class LeaderboardForBadgeSerializer(BaseModelSerializer):
    user = DefaultUserSerializer()

    class Meta:
        model = UserBadge
        fields = (
            "user",
            "created_at",
        )
