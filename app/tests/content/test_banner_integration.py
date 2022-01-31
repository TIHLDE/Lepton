from rest_framework import status

import pytest

from app.common.enums import AdminGroup
from app.util.test_utils import get_api_client

API_BANNER_URL = "/banners/"


def _get_banner_url():
    return f"{API_BANNER_URL}"


def test_get_banner_as_anonymus_user(default_client):
    "An anonymus user is not able to list banners"
    url = _get_banner_url()

    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_name, expected_status_code",
    [
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK),
        (AdminGroup.NOK, status.HTTP_403_FORBIDDEN),
        (AdminGroup.SOSIALEN, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
        (None, status.HTTP_403_FORBIDDEN),
    ],
)
def test_get_banner_as_members_in_different_groups(
    member, group_name, expected_status_code
):
    "Only HS and Index should have permission"
    url = _get_banner_url()
    client = get_api_client(user=member, group_name=group_name)

    response = client.get(url)

    assert response.status_code == expected_status_code
