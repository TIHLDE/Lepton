from rest_framework import status

import pytest

from app.common.enums import AdminGroup, GroupType, MembershipType
from app.forms.tests.form_factories import GroupFormFactory
from app.group.factories import GroupFactory, MembershipFactory
from app.util.test_utils import add_user_to_group_with_name

pytestmark = pytest.mark.django_db

FORMS_URL = "/forms/"


def _get_group_form_detail_url(form):
    return f"{FORMS_URL}{form.id}/"


def _get_group_forms_url(group):
    return f"/groups/{group.slug}/forms/"


def _get_form_post_data(group):
    return {
        "resource_type": "GroupForm",
        "title": group.name,
        "fields": [
            {
                "title": "string",
                "options": [{"title": "string", "order": 0}],
                "type": "SINGLE_SELECT",
                "required": True,
            }
        ],
        "group": group.slug,
    }


@pytest.mark.parametrize("group_name", [e.name for e in AdminGroup] + ["ikke-admin"])
def test_that_creating_group_form_as_leader_of_group_creates_the_form(
    api_client, user, group_name
):
    """Leaders of groups should be able to create group-forms"""
    group = GroupFactory.build(slug=group_name)
    add_user_to_group_with_name(
        user=user,
        group_name=group_name,
        membership_type=MembershipType.LEADER,
    )

    client = api_client(user=user)
    data = _get_form_post_data(group)

    response = client.post(FORMS_URL, data)

    expected_group_slug = group.slug.lower()
    actual_group_slug = response.json().get("group").get("slug")

    assert expected_group_slug == actual_group_slug
    assert response.status_code == status.HTTP_201_CREATED

    group.refresh_from_db()

    actual_group_form = group.forms

    assert actual_group_form.count() == 1
    assert actual_group_form.first().title == data.get("title")


@pytest.mark.parametrize("group_name", [AdminGroup.INDEX.name, AdminGroup.HS.name])
def test_that_creating_group_form_as_member_of_admin_group_creates_the_form(
    api_client, user, group_name
):
    """Members of admin-groups should be able to create group-forms"""
    group = GroupFactory.build(slug=group_name)
    add_user_to_group_with_name(
        user=user,
        group_name=group_name,
        membership_type=MembershipType.MEMBER,
    )

    client = api_client(user=user)
    data = _get_form_post_data(group)

    response = client.post(FORMS_URL, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.parametrize(
    "group_name", [AdminGroup.NOK.name, AdminGroup.SOSIALEN.name, "ikke-admin"]
)
def test_that_creating_group_form_as_member_of_group_does_not_create_the_form(
    api_client, user, group_name
):
    """Members of groups should not be able to create group-forms"""
    group = GroupFactory.build(slug=group_name)
    add_user_to_group_with_name(
        user=user,
        group_name=group_name,
        group_type=GroupType.COMMITTEE,
        membership_type=MembershipType.MEMBER,
    )

    client = api_client(user=user)
    data = _get_form_post_data(group)

    response = client.post(FORMS_URL, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "group_name", [e.name.lower() for e in AdminGroup] + ["ikke-admin"]
)
def test_that_non_group_members_can_create_group_form_for_that_group(
    api_client, user, group_name
):
    target_group = GroupFactory(slug=group_name)
    users_group = GroupFactory.build()

    client = api_client(user=user, group_name=users_group.slug)
    data = _get_form_post_data(target_group)

    response = client.post(FORMS_URL, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "membership_type, expected_amount",
    [
        (MembershipType.LEADER, 4),
        (MembershipType.MEMBER, 2),
        (None, 1),
    ],
)
def test_retrieve_list_of_group_forms_only_returns_where_is_admin_or_can_answer(
    api_client, member, group, membership_type, expected_amount
):
    """
    Leaders of group should get all forms,
    members should get all which is open for submissions
    and others should only get those who is open for submissions and not only for group members
    """
    GroupFormFactory(
        group=group, only_for_group_members=True, is_open_for_submissions=True
    )
    GroupFormFactory(
        group=group, only_for_group_members=True, is_open_for_submissions=False
    )
    GroupFormFactory(
        group=group, only_for_group_members=False, is_open_for_submissions=True
    )
    GroupFormFactory(
        group=group, only_for_group_members=False, is_open_for_submissions=False
    )

    if membership_type:
        MembershipFactory(user=member, group=group, membership_type=membership_type)

    url = _get_group_forms_url(group)

    client = api_client(user=member)
    response = client.get(url)

    assert len(response.json()) == expected_amount


@pytest.mark.parametrize(
    (
        "membership_type",
        "only_for_group_members",
        "is_open_for_submissions",
        "status_code",
        "group_type",
    ),
    [
        (MembershipType.LEADER, True, True, status.HTTP_200_OK, GroupType.COMMITTEE),
        (MembershipType.LEADER, True, False, status.HTTP_200_OK, GroupType.COMMITTEE),
        (MembershipType.LEADER, False, True, status.HTTP_200_OK, GroupType.COMMITTEE),
        (MembershipType.LEADER, False, False, status.HTTP_200_OK, GroupType.COMMITTEE),
        (MembershipType.MEMBER, True, True, status.HTTP_200_OK, GroupType.SUBGROUP),
        (MembershipType.MEMBER, True, False, status.HTTP_200_OK, GroupType.SUBGROUP),
        (MembershipType.MEMBER, False, True, status.HTTP_200_OK, GroupType.SUBGROUP),
        (MembershipType.MEMBER, False, False, status.HTTP_200_OK, GroupType.SUBGROUP),
        (MembershipType.MEMBER, True, True, status.HTTP_200_OK, GroupType.COMMITTEE),
        (
            MembershipType.MEMBER,
            True,
            False,
            status.HTTP_403_FORBIDDEN,
            GroupType.COMMITTEE,
        ),
        (MembershipType.MEMBER, False, True, status.HTTP_200_OK, GroupType.COMMITTEE),
        (
            MembershipType.MEMBER,
            False,
            False,
            status.HTTP_403_FORBIDDEN,
            GroupType.COMMITTEE,
        ),
        (None, True, True, status.HTTP_403_FORBIDDEN, GroupType.COMMITTEE),
        (None, True, False, status.HTTP_403_FORBIDDEN, GroupType.COMMITTEE),
        (None, False, True, status.HTTP_200_OK, GroupType.COMMITTEE),
        (None, False, False, status.HTTP_403_FORBIDDEN, GroupType.COMMITTEE),
    ],
)
def test_retrieve_specific_group_form(
    api_client,
    member,
    membership_type,
    only_for_group_members,
    is_open_for_submissions,
    status_code,
    group_type,
):
    """
    Leaders of group should get all forms,
    members should get if it's open for submissions
    and others should only get if it's open for submissions and not only for group members
    """
    group = GroupFactory(type=group_type)
    group_form = GroupFormFactory(
        group=group,
        only_for_group_members=only_for_group_members,
        is_open_for_submissions=is_open_for_submissions,
    )

    if membership_type:
        MembershipFactory(user=member, group=group, membership_type=membership_type)

    url = _get_group_form_detail_url(group_form)

    client = api_client(user=member)
    response = client.get(url)

    assert response.status_code == status_code
