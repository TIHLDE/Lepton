import random

from rest_framework import status

import pytest
from faker import Faker

from app.common.enums import AdminGroup, MembershipType
from app.group.factories.group_factory import GroupFactory
from app.group.factories.law_factory import LawFactory
from app.group.factories.membership_factory import MembershipFactory
from app.util.test_utils import add_user_to_group_with_name, get_api_client

faker = Faker()

GROUP_URL = "/groups/"


def _get_law_url(group, law=None):
    return (
        f"{GROUP_URL}{group.slug}/laws/{law.id}/"
        if (law)
        else f"{GROUP_URL}{group.slug}/laws/"
    )


def _get_law_data():
    return {
        "description": "very long disc",
        "paragraph": "testing",
        "amount": random.randint(1, 50),
    }


@pytest.mark.django_db
def test_list_as_anonymous_user(group, default_client):
    url = _get_law_url(group)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_retrieve_as_user(group, member):
    client = get_api_client(user=member)
    url = _get_law_url(group)
    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK),
        (AdminGroup.NOK, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
        ("Non_admin_group", status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_as_group_user(group, user, group_name, expected_status_code):
    client = get_api_client(user=user, group_name=group_name)
    url = _get_law_url(group)
    data = _get_law_data()
    response = client.post(url, data=data)
    group.refresh_from_db()

    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_create_as_group_member(user):
    group = add_user_to_group_with_name(user, group_name="name")
    client = get_api_client(user=user)
    url = _get_law_url(group)
    data = _get_law_data()
    response = client.post(url, data=data)
    group.refresh_from_db()

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_as_leader(user):
    group = GroupFactory()
    MembershipFactory(user=user, group=group, membership_type=MembershipType.LEADER)
    client = get_api_client(user=user)
    url = _get_law_url(group)
    data = _get_law_data()
    response = client.post(url, data=data)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_update_as_group_member(user):
    group = add_user_to_group_with_name(user, group_name="name")
    law = LawFactory(group=group)
    client = get_api_client(user=user)
    url = _get_law_url(group, law)
    data = _get_law_data()
    data["amount"] = 2
    response = client.put(url, data=data)
    law.refresh_from_db()
    assert law.amount == 1
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_as_leader(user):
    group = GroupFactory()
    MembershipFactory(user=user, group=group, membership_type=MembershipType.LEADER)
    law = LawFactory(group=group)
    client = get_api_client(user=user)
    url = _get_law_url(group, law)
    data = _get_law_data()
    data["amount"] = 2
    response = client.put(url, data=data)
    law.refresh_from_db()
    assert law.amount == 2
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_delete_as_group_member(user):
    group = add_user_to_group_with_name(user, group_name="name")
    law = LawFactory(group=group)
    client = get_api_client(user=user)
    url = _get_law_url(group, law)
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_as_leader(user):
    group = GroupFactory()
    MembershipFactory(user=user, group=group, membership_type=MembershipType.LEADER)
    law = LawFactory(group=group)
    client = get_api_client(user=user)
    url = _get_law_url(group, law)
    response = client.delete(url)
    assert response.status_code == status.HTTP_200_OK
