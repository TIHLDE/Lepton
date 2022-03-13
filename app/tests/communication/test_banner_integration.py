from rest_framework import status

import pytest

from app.communication.factories.banner_factory import BannerFactory

API_BANNER_URL = "/banners/"

API_VISIBLE_BANNER_URL = "/banners/visible/"


@pytest.mark.django_db
def test_get_banners_as_anonymus_user(default_client):
    "An anonymus user is not able to list all banners"
    url = API_BANNER_URL

    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_banners_as_member(member_client):
    "A member is not able to list all banners"
    url = API_BANNER_URL

    response = member_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_response_if_no_banners_are_visible(default_client):
    "A 404 response is returned if there are no visible banners"
    url = API_VISIBLE_BANNER_URL

    response = default_client.get(url)

    assert len(response.json()) == 0


@pytest.mark.django_db
def test_get_visible_banner_as_anonymus_user_when_banner_is_visible(default_client):
    "An anonymus user is able to get the banner that is visible"
    BannerFactory()
    url = API_VISIBLE_BANNER_URL

    response = default_client.get(url)

    assert response.status_code == status.HTTP_200_OK
