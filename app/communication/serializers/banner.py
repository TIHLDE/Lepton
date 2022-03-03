from rest_framework import serializers

from app.communication.models.banner import Banner


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = (
            "id",
            "title",
            "description",
            "is_visible",
            "url",
            "created_at",
            "updated_at",
            "image",
            "image_alt",
        )
