from rest_framework import serializers

from app.content.serializers.user import DefaultUserSerializer, UserSerializer
from app.group.models import Membership, MembershipHistory
from app.group.serializers.group import DefaultGroupSerializer, GroupSerializer


class MembershipSerializer(serializers.ModelSerializer):
    user = DefaultUserSerializer(read_only=True)
    group = DefaultGroupSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = (
            "user",
            "group",
            "membership_type",
            "created_at",
            "expiration_date",
        )
        read_only_fields = (
            "user",
            "group",
        )


class MembershipLeaderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = (
            "user",
            "group",
            "membership_type",
            "created_at",
            "expiration_date",
        )
        read_only_fields = (
            "user",
            "group",
        )


class UpdateMembershipSerializer(MembershipSerializer):
    class Meta(MembershipSerializer.Meta):
        fields = MembershipSerializer.Meta.fields

        read_only_fields = (
            "created_at" "user",
            "group",
        )


class MembershipHistorySerializer(serializers.ModelSerializer):
    user = DefaultUserSerializer(read_only=True)
    group = DefaultGroupSerializer(read_only=True)

    class Meta:
        model = MembershipHistory
        read_only_fields = (
            "user",
            "group",
            "membership_type",
            "start_date",
            "end_date",
        )
