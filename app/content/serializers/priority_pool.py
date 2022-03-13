from rest_framework.relations import SlugRelatedField

from app.common.serializers import BaseModelSerializer
from app.content.models import PriorityPool
from app.group.models import Group
from app.group.serializers.group import SimpleGroupSerializer


class PriorityPoolCreateSerializer(BaseModelSerializer):
    groups = SlugRelatedField(
        slug_field="slug", many=True, queryset=Group.objects.all()
    )

    class Meta:
        model = PriorityPool
        fields = ["groups"]


class PriorityPoolSerializer(BaseModelSerializer):
    groups = SimpleGroupSerializer(many=True)

    class Meta:
        model = PriorityPool
        fields = ["groups"]
