from rest_framework import status

import pytest

from app.communication.factories.banner_factory import BannerFactory

API_BANNER_URL = "/banners/"


def _get_banner_url():
    return f"{API_BANNER_URL}"


def _get_visible_banner_url():
    return f"{API_BANNER_URL}visible/"


@pytest.mark.django_db
def test_get_banners_as_anonymus_user(default_client):
    "An anonymus user is not able to list all banners"
    url = _get_banner_url()

    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_banners_as_member(member_client):
    "A member is not able to list all banners"
    url = _get_banner_url()

    response = member_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_response_if_no_banners_are_visible(default_client):
    "A 404 response is returned if there are no visible banners"
    url = _get_visible_banner_url()

    response = default_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_visible_banner_as_anonymus_user_when_banner_is_visible(default_client):
    "An anonymus user is able to get the banner that is visible"
    BannerFactory()
    url = _get_visible_banner_url()

    response = default_client.get(url)

    assert response.status_code == status.HTTP_200_OK
