from app.common.serializers import BaseModelSerializer
from app.group.models.law import Law
from app.group.serializers.group import GroupSerializer


class LawSerializer(BaseModelSerializer):
    group = GroupSerializer(read_only=True)

    class Meta:
        model = Law
        fields = ("id", "group", "description", "paragraph", "amount")

        read_only_fields = ("group",)