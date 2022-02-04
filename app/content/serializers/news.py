from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import DefaultUserSerializer

from ..models import News


class NewsSerializer(BaseModelSerializer):
    creator = DefaultUserSerializer(read_only=True)

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
            "creator",
            "body",
        )
