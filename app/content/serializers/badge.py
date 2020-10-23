from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from app.content.models import Badge, User, UserBadge


class BadgeSerializer(serializers.ModelSerializer):
    total_completion_percentage = SerializerMethodField()

    class Meta:
        model = Badge
        fields = [
            "id",
            "title",
            "description",
            "total_completion_percentage",
            "image",
            "image_alt",
        ]

    def get_total_completion_percentage(self, obj):
        total_user_count = User.objects.all().count()
        badge_completion_count = UserBadge.objects.filter(badge=obj).count()
        return badge_completion_count / total_user_count * 100
