from rest_framework import status

import pytest

from app.common.enums import AdminGroup, MembershipType
from app.group.factories.fine_factory import FineFactory
from app.group.factories.group_factory import GroupFactory
from app.group.factories.membership_factory import MembershipFactory
from app.util.test_utils import add_user_to_group_with_name, get_api_client

GROUP_URL = "/group/"


def _get_fine_url(group, fine=None):
    return (
        f"{GROUP_URL}{group.slug}/fines/{fine.id}/"
        if (fine)
        else f"{GROUP_URL}{group.slug}/fines/"
    )


def _get_fine_data(user, approved=False, payed=False, description=None):
    return {
        "created_by": user.user_id,
        "amount": 1,
        "approved": approved,
        "payed": payed,
        "description": "Test" if not description else description,
        "user": [user.user_id],
    }


def _get_fine_data_update_data(fine):
    return {
        "amount": 1,
        "approved": fine.approved,
        "payed": fine.payed,
        "description": fine.description,
    }


@pytest.mark.django_db
def test_list_as_anonymous_user(group, default_client):
    url = _get_fine_url(group)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_retrieve_as_user(group, member):
    client = get_api_client(user=member)
    url = _get_fine_url(group)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


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
    url = _get_fine_url(group)
    data = _get_fine_data(user=user)
    response = client.post(url, data=data)
    group.refresh_from_db()

    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_create_as_group_member(user):
    group = add_user_to_group_with_name(user, group_name="name")
    client = get_api_client(user=user)
    url = _get_fine_url(group)
    data = _get_fine_data(user=user)
    response = client.post(url, data=data)
    group.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_update_as_fines_admin(user):
    group = GroupFactory(fines_admin=user)
    MembershipFactory(user=user, group=group)
    fine = FineFactory(payed=False, group=group)
    client = get_api_client(user=user)
    url = _get_fine_url(group, fine)
    data = _get_fine_data_update_data(fine)
    data["payed"] = True
    response = client.put(url, data=data)
    assert not fine.payed
    fine.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert fine.payed


@pytest.mark.django_db
def test_update_as_leader(user):
    group = GroupFactory()
    MembershipFactory(user=user, group=group, membership_type=MembershipType.LEADER)
    fine = FineFactory(payed=False, group=group)
    client = get_api_client(user=user)
    url = _get_fine_url(group, fine)
    data = _get_fine_data_update_data(fine)
    data["payed"] = True
    response = client.put(url, data=data)
    assert not fine.payed
    fine.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert fine.payed


@pytest.mark.django_db
def test_update_as_member(user, group):
    MembershipFactory(user=user, group=group)
    fine = FineFactory(payed=False, group=group)
    client = get_api_client(user=user)
    url = _get_fine_url(group, fine)
    data = _get_fine_data_update_data(fine)
    data["payed"] = True
    response = client.put(url, data=data)
    fine.refresh_from_db()
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_as_user(member, group):
    fine = FineFactory(payed=False, group=group)
    client = get_api_client(user=member)
    url = _get_fine_url(group, fine)
    data = _get_fine_data_update_data(fine)
    data["payed"] = True
    response = client.put(url, data=data)
    fine.refresh_from_db()
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_as_group_leader(user, group):
    MembershipFactory(user=user, group=group, membership_type=MembershipType.LEADER)
    fine = FineFactory(group=group)
    client = get_api_client(user=user)
    url = _get_fine_url(group, fine)
    response = client.delete(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_delete_as_group_fines_admin(user):
    group = GroupFactory(fines_admin=user)
    MembershipFactory(user=user, group=group)
    fine = FineFactory(group=group)
    client = get_api_client(user=user)
    url = _get_fine_url(group, fine)
    response = client.delete(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_delete_as_member(user):
    group = GroupFactory()
    MembershipFactory(user=user, group=group)
    fine = FineFactory(group=group)
    client = get_api_client(user=user)
    url = _get_fine_url(group, fine)
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
