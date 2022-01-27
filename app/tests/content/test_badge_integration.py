from datetime import timedelta

from rest_framework import status

import pytest

from app.content.factories.badge_factory import BadgeFactory
from app.util.test_utils import get_api_client
from app.util.utils import now

API_BADGE_BASE_URL = "/badges/"


def _get_badge_leaderboard_url():
    return f"{API_BADGE_BASE_URL}leaderboard/"


def _get_badge_specific_leaderboard_url(badge):
    return f"{API_BADGE_BASE_URL}{badge.id}/leaderboard/"


def _get_user_badge_url():
    return f"/users/me{API_BADGE_BASE_URL}"


def _get_badge_flag(badge):
    return {"flag": badge.flag}


@pytest.mark.django_db
def test_get_badge_leaderboard_as_anonymous_user(default_client):
    """An anonymous user should not be able to see the leaderboard"""

    url = _get_badge_leaderboard_url()
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_badge_spesific_leaderboard_as_anonymous_user(default_client, badge):
    """An anonymous user should not be able to see badge-specific leaderboard"""

    url = _get_badge_specific_leaderboard_url(badge)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_request_for_user_badges_as_anonymous_user(default_client):
    """An anonymous user should not be able to do a get request for a user badge"""

    url = _get_user_badge_url()
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_user_badge_as_member(member, badge):
    """All members should be able to create a user badge for themselves"""

    url = _get_user_badge_url()
    client = get_api_client(user=member)
    data = _get_badge_flag(badge)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_user_badge_for_already_existing_user_badges(member, badge):
    """User badges that already exist can not be created and throws 409 unique-together exception"""

    url = _get_user_badge_url()
    client = get_api_client(user=member)
    data = _get_badge_flag(badge)
    client.post(url, data)
    response = client.post(url, data)
    detail = response.json().get("detail")

    assert response.status_code == status.HTTP_409_CONFLICT
    assert detail == "Some values are supposed to be unique but are not."


@pytest.mark.django_db
def test_create_user_badge_for_non_existent_badge(member):
    """Badge has to exist for a User Badge to be created. Therefore the view returns a 404"""

    url = _get_user_badge_url()
    client = get_api_client(user=member)
    data = {"flag": "flag_unlike_anything_else"}
    response = client.post(url, data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("active_from", "active_to", "expected_status_code", "expected_detail"),
    [
        (
            now() + timedelta(1),
            None,
            status.HTTP_400_BAD_REQUEST,
            "Badgen er ikke aktiv",
        ),
        (
            None,
            now() - timedelta(1),
            status.HTTP_400_BAD_REQUEST,
            "Badgen er ikke aktiv",
        ),
        (
            now() + timedelta(1),
            now() + timedelta(2),
            status.HTTP_400_BAD_REQUEST,
            "Badgen er ikke aktiv",
        ),
        (
            now() - timedelta(2),
            now() - timedelta(1),
            status.HTTP_400_BAD_REQUEST,
            "Badgen er ikke aktiv",
        ),
        (
            now() - timedelta(1),
            now() - timedelta(2),
            status.HTTP_400_BAD_REQUEST,
            "Badgen er ikke aktiv",
        ),
        (
            now() - timedelta(1),
            now() + timedelta(1),
            status.HTTP_200_OK,
            "Badge fullført!",
        ),
        (now(), None, status.HTTP_200_OK, "Badge fullført!"),
        (None, now() + timedelta(1), status.HTTP_200_OK, "Badge fullført!"),
        (None, None, status.HTTP_200_OK, "Badge fullført!"),
    ],
)
def test_create_user_badge_for_different_active_dates(
    member, active_from, active_to, expected_status_code, expected_detail
):
    """Tests several arguments for active_from and active_to dates and checks whether response is expected.
       Badge is not active if active_from is later than now or active_to is earlier than now.
       If active_to/from is None, it is treated as infinitly far in the past for active_from and in the future for active_to."""

    badge = BadgeFactory(active_to=active_to, active_from=active_from)
    url = _get_user_badge_url()
    client = get_api_client(user=member)
    data = _get_badge_flag(badge)

    response = client.post(url, data)
    detail = response.json().get("detail")

    assert response.status_code == expected_status_code
    assert detail == expected_detail
