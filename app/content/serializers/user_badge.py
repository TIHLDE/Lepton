from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.content.models import User, UserBadge


class UserBadgeSerializer(BaseModelSerializer):
    user = serializers.SerializerMethodField()
    badge = serializers.SerializerMethodField()

    class Meta:
        model = UserBadge
        fields = ["user", "badge"]

    def get_user(self, obj):
        """ Gets the necessary info from user """
        user = obj.user
        return {
            "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

    def get_badge(self, obj):
        """ Gets the necessary info from badge """
        badge = obj.badge
        return {
            "id": badge.id,
            "title": badge.title,
            "description": badge.description,
            "image": badge.image,
            "image_alt": badge.image_alt,
        }


class LeaderboardSerializer(BaseModelSerializer):
    user = serializers.SerializerMethodField()
    number_of_badges = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "user",
            "number_of_badges",
        )

    def get_user(self, obj):
        """ Gets the necessary info from user """
        return {
            "user_id": obj.user_id,
            "first_name": obj.first_name,
            "last_name": obj.last_name,
            "user_class": obj.user_class,
            "user_study": obj.user_study,
        }

    def get_number_of_badges(self, obj):
        return len(UserBadge.objects.filter(user=obj))
