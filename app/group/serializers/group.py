from rest_framework import serializers

from dry_rest_permissions.generics import DRYPermissionsField

from app.common.enums import MembershipType
from app.common.serializers import BaseModelSerializer
from app.content.models.user import User
from app.content.serializers.user import DefaultUserSerializer
from app.group.models import Group, Membership


class GroupSerializer(BaseModelSerializer):

    leader = serializers.SerializerMethodField()
    permissions = DRYPermissionsField(actions=["write", "read"], object_only=True)
    fines_admin = DefaultUserSerializer(read_only=True)

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
            "fine_info",
            "image",
            "image_alt",
        )

    def get_leader(self, obj):
        try:
            leader = obj.memberships.get(
                group__slug=obj.slug, membership_type=MembershipType.LEADER
            )
            return DefaultUserSerializer(leader.user).data
        except Membership.DoesNotExist:
            return None

    def update(self, instance, validated_data):
        fines_admin = self.context["request"].data.get("fines_admin", None)
        if not fines_admin:
            instance.fines_admin = None
        else:
            instance.fines_admin = User.objects.get(user_id=fines_admin)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        fines_admin = self.context["request"].data.get("fines_admin", None)
        if not fines_admin:
            fines_admin = None
        else:
            fines_admin = User.objects.get(user_id=fines_admin)

        return Group(fines_admin=fines_admin, **validated_data)


class DefaultGroupSerializer(BaseModelSerializer):
    class Meta:
        model = Group
        fields = (
            "name",
            "slug",
            "description",
            "contact_email",
            "type",
            "image",
            "image_alt",
        )
