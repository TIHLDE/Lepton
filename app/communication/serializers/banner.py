from rest_framework import serializers

from app.communication.models.banner import Banner


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = (
            "id",
            "title",
            "description",
            "visible_from",
            "visible_until",
            "url",
            "created_at",
            "updated_at",
            "image",
            "image_alt",
            "is_visible",
            "is_expired",
        )
