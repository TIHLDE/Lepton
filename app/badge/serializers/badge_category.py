from app.badge.models import BadgeCategory
from app.common.serializers import BaseModelSerializer


class BadgeCategorySerializer(BaseModelSerializer):
    class Meta:
        model = BadgeCategory
        fields = [
            "id",
            "name",
            "description",
            "image",
            "image_alt",
        ]
