from rest_framework import fields

from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import DefaultUserSerializer
from app.group.models import group
from app.group.models.fine import Fine
from app.group.serializers.group import DefaultGroupSerializer


class FineSerializer(BaseModelSerializer):
    user = DefaultUserSerializer(read_only=True)
    group = DefaultGroupSerializer(read_only=True)

    class Meta:
        model = Fine
        fields = ("id", "user", "group", "amount", "approved", "payed", "description")

        read_only_fields = (
            "user",
            "group",
        )


class MembershipFineSerializer(BaseModelSerializer):
    class Meta:
        model = Fine
        fields = ("id", "amount", "approved", "payed", "description")
