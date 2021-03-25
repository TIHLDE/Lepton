from app.common.serializers import BaseModelSerializer

from ..models import News


class NewsSerializer(BaseModelSerializer):
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
