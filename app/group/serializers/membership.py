from rest_framework import serializers

from app.content.serializers.user import DefaultUserSerializer
from app.group.models import Membership, MembershipHistory
from app.group.serializers.group import DefaultGroupSerializer


class MembershipSerializer(serializers.ModelSerializer):
    user = DefaultUserSerializer()
    group = DefaultGroupSerializer()

    class Meta:
        model = Membership
        fields = (
            "user",
            "group",
            "membership_type",
            "created_at",
            "expiration_date",
        )


class UpdateMembershipSerializer(MembershipSerializer):
    class Meta(MembershipSerializer.Meta):
        fields = MembershipSerializer.Meta.fields
        read_only_fields = ("user", "group", "created_at")


class MembershipHistorySerializer(serializers.ModelSerializer):
    user = DefaultUserSerializer()
    group = DefaultGroupSerializer()

    class Meta:
        model = MembershipHistory
        read_only_fields = (
            "user",
            "group",
            "membership_type",
            "start_date",
            "end_date",
        )
