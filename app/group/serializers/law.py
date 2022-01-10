from app.common.serializers import BaseModelSerializer
from app.group.models.law import Law


class LawSerializer(BaseModelSerializer):
    class Meta:
        model = Law
        fields = ("id", "description", "paragraph", "title", "amount")
