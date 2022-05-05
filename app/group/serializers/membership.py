from app.common.serializers import BaseModelSerializer
from app.content.models.user import User
from app.content.serializers.user import (
    DefaultUserSerializer,
    UserListSerializer,
)
from app.group.models import Membership, MembershipHistory
from app.group.models.group import Group
from app.group.serializers.group import SimpleGroupSerializer


class BaseMembershipSerializer(BaseModelSerializer):
    group = SimpleGroupSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = (
            "group",
            "membership_type",
            "created_at",
            "expiration_date",
        )
        read_only_fields = ("group",)


class MembershipSerializer(BaseMembershipSerializer):
    user = DefaultUserSerializer(read_only=True)

    class Meta:
        model = Membership
        fields = BaseMembershipSerializer.Meta.fields + ("user",)
        read_only_fields = BaseMembershipSerializer.Meta.read_only_fields + ("user",)


class MembershipLeaderSerializer(BaseModelSerializer):
    user = UserListSerializer(read_only=True)
    group = SimpleGroupSerializer(read_only=True)

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
            "created_at",
            "user",
            "group",
        )


class MembershipHistorySerializer(BaseModelSerializer):
    user = DefaultUserSerializer(read_only=True)
    group = SimpleGroupSerializer(read_only=True)

    class Meta:
        model = MembershipHistory
        fields = (
            "id",
            "user",
            "group",
            "membership_type",
            "start_date",
            "end_date",
        )
        read_only_fields = (
            "id",
            "user",
            "group",
        )

    def create(self, validated_data):
        request = self.context["request"]

        user = User.objects.get(user_id=request.data.get("user", None))
        group = Group.objects.get(slug=request.parser_context["kwargs"]["slug"])

        return MembershipHistory.objects.create(
            user=user, group=group, **validated_data
        )
