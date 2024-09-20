from rest_framework import serializers

from dry_rest_permissions.generics import DRYPermissionsField

from app.common.enums import (
    NativeGroupType as GroupType,
    MembershipType
)
from app.common.serializers import BaseModelSerializer
from app.content.models.user import User
from app.content.serializers.user import DefaultUserSerializer
from app.group.models import Group, Membership


class SimpleGroupSerializer(BaseModelSerializer):
    viewer_is_member = serializers.SerializerMethodField()

    class Meta:
        model = Group
        lookup_field = "slug"
        fields = (
            "name",
            "slug",
            "type",
            "viewer_is_member",
            "image",
            "image_alt",
            "fines_activated",
        )

    def get_viewer_is_member(self, obj):
        request = self.context.get("request", None)
        if request and request.user:
            return request.user.is_member_of(obj)
        return False


class GroupListSerializer(SimpleGroupSerializer):

    leader = serializers.SerializerMethodField()

    class Meta:
        model = SimpleGroupSerializer.Meta.model

        lookup_field = SimpleGroupSerializer.Meta.lookup_field
        fields = SimpleGroupSerializer.Meta.fields + (
            "contact_email",
            "leader",
        )

    def get_leader(self, obj):
        try:
            leader = obj.memberships.get(
                group__slug=obj.slug, membership_type=MembershipType.LEADER
            )
            return DefaultUserSerializer(leader.user).data
        except Membership.DoesNotExist:
            return None


class GroupSerializer(GroupListSerializer):

    permissions = DRYPermissionsField(
        actions=["write", "read", "group_form"], object_only=True
    )
    fines_admin = DefaultUserSerializer(read_only=True)

    class Meta:
        model = GroupListSerializer.Meta.model

        lookup_field = GroupListSerializer.Meta.lookup_field
        fields = GroupListSerializer.Meta.fields + (
            "description",
            "permissions",
            "fines_admin",
            "fines_activated",
            "fine_info",
        )

    def get_fine_admin_user(self):
        fines_admin_id = self.context["request"].data.get("fines_admin", None)
        if not fines_admin_id:
            fines_admin = None
        else:
            fines_admin = User.objects.get(user_id=fines_admin_id)
        return fines_admin

    def update(self, instance, validated_data):
        instance.fines_admin = self.get_fine_admin_user()
        return super().update(instance, validated_data)

    def create(self, validated_data):
        fines_admin = self.get_fine_admin_user()
        return Group.objects.create(fines_admin=fines_admin, **validated_data)


class GroupStatisticsSerializer(BaseModelSerializer):
    studyyears = serializers.SerializerMethodField()
    studies = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ("studyyears", "studies")

    def get_studyyears(self, obj, *args, **kwargs):
        return filter(
            lambda studyyear: studyyear["amount"] > 0,
            map(
                lambda group: {
                    "studyyear": group.name,
                    "amount": obj.memberships.filter(
                        user__memberships__group=group
                    ).count(),
                },
                Group.objects.filter(type=GroupType.STUDYYEAR),
            ),
        )

    def get_studies(self, obj, *args, **kwargs):
        return filter(
            lambda study: study["amount"] > 0,
            map(
                lambda group: {
                    "study": group.name,
                    "amount": obj.memberships.filter(
                        user__memberships__group=group
                    ).count(),
                },
                Group.objects.filter(type=GroupType.STUDY),
            ),
        )
