from django.db.transaction import atomic
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from app.common.enums import (
    AdminGroup,
    NativeGroupType as GroupType,
    NativeMembershipType as MembershipType
)
from app.group.models import Group, Membership


def get_api_client(user=None, group_name=None):
    client = APIClient()
    if user:
        if group_name:
            add_user_to_group_with_name(user, group_name)
        client.force_authenticate(user=user)
        token = Token.objects.get(user_id=user.user_id)
        client.credentials(HTTP_X_CSRF_TOKEN=token)

    return client


@atomic
def add_user_to_group_with_name(
    user, group_name, group_type=None, membership_type=MembershipType.MEMBER
):
    if not group_type:
        group_type = get_group_type_from_group_name(group_name)
    group = Group.objects.get_or_create(name=group_name, type=group_type)[0]
    Membership.objects.get_or_create(
        group=group, user=user, membership_type=membership_type
    )
    return group


def get_group_type_from_group_name(group_name):
    if group_name == AdminGroup.HS:
        return GroupType.BOARD
    elif group_name in AdminGroup.all():
        return GroupType.SUBGROUP
    return GroupType.COMMITTEE
