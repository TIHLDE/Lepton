from rest_framework import serializers

from app.common.enums import MembershipType
from app.common.serializers import BaseModelSerializer
from app.group.models import Group, Membership


class DefaultGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("name",)


class GroupSerializer(BaseModelSerializer):

    leader = serializers.SerializerMethodField()

    class Meta:
        model = Group
        lookup_field = "slug"
        fields = (
            "name",
            "slug",
            "description",
            "contact_email",
            "type",
            "permissions",
            "leader",
        )

    def get_leader(self, obj):
        try:
            leader = obj.membership.get(
                group__slug=obj.slug, membership_type=MembershipType.LEADER
            )
            return {
                "user_id": leader.user.user_id,
                "first_name": leader.user.first_name,
                "last_name": leader.user.last_name,
                "image": leader.user.image,
            }
        except Membership.DoesNotExist:
            return None
