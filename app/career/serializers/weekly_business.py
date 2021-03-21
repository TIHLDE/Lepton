from app.career.models import WeeklyBusiness
from app.common.serializers import BaseModelSerializer


class WeeklyBusinessSerializer(BaseModelSerializer):
    class Meta:
        model = WeeklyBusiness
        fields = (
            "id",
            "created_at",
            "updated_at",
            "image",
            "image_alt",
            "business_name",
            "body",
            "year",
            "week",
        )
        validators = []
