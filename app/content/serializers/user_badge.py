from rest_framework import serializers

from app.content.models import UserBadge


class UserBadgeSerializer(serializers.ModelSerializer):
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
