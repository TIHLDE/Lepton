from rest_framework import serializers

from ..models import News


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = (
            "id",
            "created_at",
            "updated_at",
            "image",
            "image_alt",
            "title",
            "header",
            "body",
        )
