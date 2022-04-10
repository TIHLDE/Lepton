from datetime import timedelta

from rest_framework import status

import pytest

from app.communication.factories.banner_factory import BannerFactory
from app.util.utils import now

API_BANNER_URL = "/banners/"

API_VISIBLE_BANNER_URL = "/banners/visible/"


@pytest.mark.django_db
def test_get_banners_as_anonymus_user(default_client):
    "An anonymus user is not able to list all banners"
    response = default_client.get(API_BANNER_URL)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_banners_as_member(member_client):
    "A member is not able to list all banners"
    response = member_client.get(API_BANNER_URL)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_en_empty_list_is_returned_if_no_banners_are_visible(default_client):
    "An empty list is returned if there are no visible banners"
    response = default_client.get(API_VISIBLE_BANNER_URL)

    assert len(response.json()) == 0


@pytest.mark.django_db
def test_get_visible_banner_as_anonymus_user_when_banner_is_visible(default_client):
    "An anonymus user is able to get the banner that is visible"
    BannerFactory()

    response = default_client.get(API_VISIBLE_BANNER_URL)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "visible_from, visible_until, visible_banners",
    [
        (now() + timedelta(hours=1), now() + timedelta(hours=2), 0),
        (now(), now() + timedelta(2), 1),
        (now() - timedelta(hours=1), now() + timedelta(hours=1), 1),
        (now() - timedelta(hours=2), now() - timedelta(hours=1), 0),
    ],
)
@pytest.mark.django_db
def test_only_visible_banner_is_shown(
    visible_from, visible_until, visible_banners, default_client
):
    """A banner is returned if it is visible"""
    BannerFactory(visible_from=visible_from, visible_until=visible_until)

    response = default_client.get(API_VISIBLE_BANNER_URL)

    assert len(response.json()) == visible_banners
