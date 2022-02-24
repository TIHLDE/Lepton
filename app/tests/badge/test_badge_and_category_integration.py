from datetime import timedelta

from rest_framework import status

import pytest

from app.badge.factories import BadgeFactory
from app.util.utils import now

API_BADGE_BASE_URL = "/badges/"


def _get_badges_url():
    return f"{API_BADGE_BASE_URL}"


def _get_badge_categories_url():
    return f"{API_BADGE_BASE_URL}categories/"


@pytest.mark.django_db
def test_get_badges_as_anonymus_user(default_client):
    """Anonymus user can not get badges"""

    url = _get_badges_url()

    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_badges_as_member(member_client):
    """Member can get badges"""

    url = _get_badges_url()

    response = member_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_badge_categories_as_anonymus_user(default_client):
    """Anonymus user can not get badge categories"""

    url = _get_badge_categories_url()

    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_badge_categories_as_member(member_client):
    """Member can get badge categories"""

    url = _get_badge_categories_url()

    response = member_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_no_badges_are_shown_when_none_are_public(api_client, admin_user):
    """Not even admin can list non public badges.
       Therefore only one badge is displayed"""

    BadgeFactory(active_to=now() + timedelta(days=1))
    BadgeFactory(active_from=now() + timedelta(days=1))
    BadgeFactory()
    url = _get_badges_url()
    admin_client = api_client(admin_user)

    response = admin_client.get(url)
    results = response.json().get("results")
    print(results)

    assert len(results) == 1
