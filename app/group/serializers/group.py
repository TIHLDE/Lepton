from rest_framework import serializers

from dry_rest_permissions.generics import DRYPermissionsField

from app.common.enums import MembershipType
from app.common.serializers import BaseModelSerializer
from app.content.models.user import User
from app.content.serializers.user import DefaultUserSerializer
from app.group.models import Group, Membership


class GroupSerializer(BaseModelSerializer):

    viewer_is_member = serializers.SerializerMethodField()
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
            "viewer_is_member",
        )

    def get_leader(self, obj):
        try:
            leader = obj.memberships.get(
                group__slug=obj.slug, membership_type=MembershipType.LEADER
            )
            return DefaultUserSerializer(leader.user).data
        except Membership.DoesNotExist:
            return None

    def get_fine_admin_user(self):
        fines_admin_id = self.context["request"].data.get("fines_admin", None)
        if not fines_admin_id:
            fines_admin = None
        else:
            fines_admin = User.objects.get(user_id=fines_admin_id)
        return fines_admin

    def get_viewer_is_member(self, obj):
        request = self.context.get("request", None)
        if request and request.user:
            return request.user.is_member_of(obj)
        return False

    def update(self, instance, validated_data):
        instance.fines_admin = self.get_fine_admin_user()
        return super().update(instance, validated_data)

    def create(self, validated_data):
        fines_admin = self.get_fine_admin_user()
        return Group.objects.create(fines_admin=fines_admin, **validated_data)
