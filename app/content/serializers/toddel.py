from app.common.serializers import BaseModelSerializer
from app.content.models import Toddel


class ToddelSerializer(BaseModelSerializer):
    class Meta:
        model = Toddel
        fields = (
            "created_at",
            "updated_at",
            "image",
            "title",
            "pdf",
            "edition",
            "published_at",
        )
