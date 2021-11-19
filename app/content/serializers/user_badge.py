from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.content.models import UserBadge
from app.content.serializers.user import DefaultUserSerializer


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


class UserBadgeLeaderboardSerializer(BaseModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = UserBadge
        fields = ("user", "created_at")

    def get_user(self, obj):
        return DefaultUserSerializer(
            obj.user
        ).data  # TODO Tror dette er feil metode men klarte ikke å løse det på en annen måte
