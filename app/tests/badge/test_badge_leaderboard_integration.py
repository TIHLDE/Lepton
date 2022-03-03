from rest_framework import status

import pytest

API_BADGE_BASE_URL = "/badges/"


def _get_badge_leaderboard_url():
    return f"{API_BADGE_BASE_URL}leaderboard/"


def _get_badge_specific_leaderboard_url(badge):
    return f"{API_BADGE_BASE_URL}{badge.id}/leaderboard/"


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
def test_get_badge_leaderboard_as_member(member_client):
    """An anonymous user should not be able to see the leaderboard"""

    url = _get_badge_leaderboard_url()
    response = member_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_badge_spesific_leaderboard_as_member(member_client, badge):
    """An anonymous user should not be able to see badge-specific leaderboard"""

    url = _get_badge_specific_leaderboard_url(badge)
    response = member_client.get(url)

    assert response.status_code == status.HTTP_200_OK
