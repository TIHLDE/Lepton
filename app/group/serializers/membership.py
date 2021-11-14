from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import (
    DefaultUserSerializer,
    UserListSerializer,
)
from app.group.models import Membership, MembershipHistory
from app.group.serializers.fine import MembershipFineSerializer
from app.group.serializers.group import DefaultGroupSerializer


class MembershipSerializer(BaseModelSerializer):
    user = DefaultUserSerializer(read_only=True)
    group = DefaultGroupSerializer(read_only=True)
    fines = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = (
            "user",
            "group",
            "membership_type",
            "created_at",
            "expiration_date",
            "fines",
        )
        read_only_fields = (
            "user",
            "group",
        )

    def get_fines(self, obj):
        return MembershipFineSerializer(
            obj.user.fines.filter(group=obj.group), many=True
        ).data


class MembershipLeaderSerializer(BaseModelSerializer):
    user = UserListSerializer(read_only=True)
    group = DefaultGroupSerializer(read_only=True)
    fines = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = (
            "user",
            "group",
            "membership_type",
            "created_at",
            "expiration_date",
            "fines",
        )
        read_only_fields = (
            "user",
            "group",
        )

    def get_fines(self, obj):
        return MembershipFineSerializer(
            obj.user.fines.filter(group=obj.group), many=True
        ).data


class UpdateMembershipSerializer(MembershipSerializer):
    class Meta(MembershipSerializer.Meta):
        fields = MembershipSerializer.Meta.fields

        read_only_fields = (
            "created_at",
            "user",
            "group",
        )


class MembershipHistorySerializer(BaseModelSerializer):
    user = DefaultUserSerializer(read_only=True)

    class Meta:
        model = MembershipHistory
        fields = (
            "user",
            "membership_type",
            "start_date",
            "end_date",
        )
        read_only_fields = fields
