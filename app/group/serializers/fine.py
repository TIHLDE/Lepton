from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.content.models.user import User
from app.content.serializers.user import DefaultUserSerializer
from app.group.models.fine import Fine
from app.group.models.group import Group
from app.group.serializers.group import DefaultGroupSerializer


class FineListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        validated_data = validated_data[0]
        group = Group.objects.get(slug=self.context["group_slug"])
        users = User.objects.filter(user_id__in=self.context["user_ids"])
        created_by = User.objects.get(user_id=self.context["created_by"])
        fines = [
            Fine(group=group, created_by=created_by, user=user, **validated_data)
            for user in users
        ]
        return Fine.objects.bulk_create(fines)


class FineSerializer(BaseModelSerializer):
    user = DefaultUserSerializer(read_only=True)
    group = DefaultGroupSerializer(read_only=True)

    class Meta:
        model = Fine
        list_serializer_class = FineListSerializer
        fields = ("id", "user", "group", "amount", "approved", "payed", "description")

        read_only_fields = (
            "user",
            "group",
        )

    def create(self, validated_data):
        group = Group.objects.get(slug=self.context["group_slug"])
        user = User.objects.get(user_id=self.context["user_id"])
        created_by = User.objects.get(user_id=self.context["created_by"])
        return Fine.objects.create(
            group=group, created_by=created_by, user=user, **validated_data
        )


class MembershipFineSerializer(BaseModelSerializer):
    class Meta:
        model = Fine
        fields = ("id", "amount", "approved", "payed", "description")
