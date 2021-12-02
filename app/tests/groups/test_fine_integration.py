

from rest_framework import status
import factory

from app.common.enums import AdminGroup
from app.tests.groups.test_group_intergration import GROUP_URL
from app.util.test_utils import add_user_to_group_with_name, get_api_client
import pytest


GROUP_URL = "/group/"

def _get_fine_url(group, fine=None):
    return f"{GROUP_URL}{group.slug}/fines/{fine.id}" if (fine) else f"{GROUP_URL}{group.slug}/fines/"


def _get_fine_data(user, approved=False, payed=False, description=None):
    return  {
        "amount": 1,
        "approved": approved,
        "payed": payed,
        "description": "Test" if not description else description,
        "user": [
            user.user_id
        ]
}

@pytest.mark.django_db
def test_list_as_anonymous_user(group, default_client):
    """Tests if an anonymous user can list fines for a group"""

    url = _get_fine_url(group)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    
@pytest.mark.django_db
def test_retrieve_as_user(group, user):
    """Tests if an non member user can't retrieve fines for a group"""
    client = get_api_client(user=user)
    url = _get_fine_url(group)
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
def test_create_as_group_user(
    group, user, group_name, expected_status_code
):
    """Tests if diffierent groups ability to update a group"""

    client = get_api_client(user=user, group_name=group_name)
    url = _get_fine_url(group)
    data = _get_fine_data(user=user)
    response = client.post(url, data=data)
    group.refresh_from_db()

    assert response.status_code == expected_status_code
    
@pytest.mark.django_db
def test_create_as_group_member(user):
    """Tests if diffierent groups ability to update a group"""
    group = add_user_to_group_with_name(user, group_name="name")
    client = get_api_client(user=user)
    url = _get_fine_url(group)
    data = _get_fine_data(user=user)
    response = client.post(url, data=data)
    group.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    
    
