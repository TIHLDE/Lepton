from rest_framework import serializers

from dry_rest_permissions.generics import DRYPermissionsField

from app.common.enums import MembershipType
from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import DefaultUserSerializer
from app.group.models import Group, Membership


class GroupSerializer(BaseModelSerializer):

    leader = serializers.SerializerMethodField()
    permissions = DRYPermissionsField(actions=["write", "read"], object_only=True)

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
            "fines_admin",
            "fines_activated",
        )
        read_only_fields = ("fines_admin",)

    def get_leader(self, obj):
        try:
            leader = obj.memberships.get(
                group__slug=obj.slug, membership_type=MembershipType.LEADER
            )
            return DefaultUserSerializer(leader.user).data
        except Membership.DoesNotExist:
            return None
