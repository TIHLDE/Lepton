from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from app.common.serializers import BaseModelSerializer
from app.content.models import Badge, User, UserBadge
from app.content.serializers.user import DefaultUserSerializer


class BadgeSerializer(BaseModelSerializer):
    total_completion_percentage = SerializerMethodField()

    class Meta:
        model = Badge
        fields = [
            "id",
            "title",
            "description",
            "total_completion_percentage",
            "badge_category",
            "active_from",
            "active_to",
            "image",
            "image_alt",
        ]

    def get_total_completion_percentage(self, obj):
        total_user_count = User.objects.all().count()
        badge_completion_count = UserBadge.objects.filter(badge=obj).count()
        return badge_completion_count / total_user_count * 100


class LeaderboardSerializer(BaseModelSerializer):
    number_of_badges = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "user",
            "number_of_badges",
        )

    def get_user(self, obj):
        return DefaultUserSerializer(obj).data

    def get_number_of_badges(self, obj):
        return UserBadge.objects.filter(user=obj).count()


class LeaderboardForBadgeSerializer(BaseModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = UserBadge
        fields = (
            "user",
            "created_at",
        )

    def get_user(self, obj):
        return DefaultUserSerializer(obj.user).data
