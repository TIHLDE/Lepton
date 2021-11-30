from rest_framework import status

import pytest

from app.common.enums import AdminGroup
from app.forms.tests.form_factories import GroupFormFactory
from app.group.factories import GroupFactory

pytestmark = pytest.mark.django_db


GROUP_URL = "/groups"


def _get_group_form_url(group=None):
    return f"{GROUP_URL}/{group.slug}/forms/"


def test_list_as_member_returns_all_of_the_specified_groups_forms(api_client, member):

    batch_size = 2
    group = GroupFactory(slug=AdminGroup.HS)
    GroupFormFactory.create_batch(batch_size, group=group)
    GroupFormFactory.create_batch(batch_size, group=GroupFactory())

    url = _get_group_form_url(group)
    client = api_client(user=member)

    response = client.get(url)
    response_data = response.json()

    actual_group_slugs = [g.get("group").get("slug") for g in response_data]

    assert len(response_data) == batch_size
    assert all(slug == group.slug for slug in actual_group_slugs)


def test_list_as_member_returns_http_200(api_client, member):
    group = GroupFactory(slug=AdminGroup.HS)

    url = _get_group_form_url(group)
    client = api_client(user=member)

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


def test_list_as_non_member_is_forbidden(api_client, user):
    group = GroupFactory(slug=AdminGroup.HS)

    url = _get_group_form_url(group)
    client = api_client(user=user)
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
