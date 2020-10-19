from rest_framework import serializers

from ..models import Badge


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["id", "title", "description", "image", "image_alt"]
