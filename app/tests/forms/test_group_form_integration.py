from rest_framework import status

import pytest

from app.common.enums import AdminGroup, MembershipType
from app.group.factories import GroupFactory, MembershipFactory
from app.util.test_utils import add_user_to_group_with_name

pytestmark = pytest.mark.django_db

FORMS_URL = "/forms/"


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
        user=user, group_name=group_name, membership_type=MembershipType.LEADER
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
        user=user, group_name=group_name, membership_type=MembershipType.MEMBER
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
        user=user, group_name=group_name, membership_type=MembershipType.MEMBER
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
