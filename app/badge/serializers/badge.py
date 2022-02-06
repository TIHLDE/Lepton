from rest_framework import serializers

from app.badge.models import Badge, UserBadge
from app.common.serializers import BaseModelSerializer
from app.badge.models import Badge, UserBadge
from app.content.models import User


class BadgeSerializer(BaseModelSerializer):
    total_completion_percentage = serializers.SerializerMethodField()

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
