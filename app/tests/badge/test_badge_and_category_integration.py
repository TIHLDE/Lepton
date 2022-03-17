from datetime import timedelta

from rest_framework import status
from app.content.models.user import User
from app.group.models.membership import Membership
from app.tests.conftest import member_client
from app.tests.content.test_user_integration import user_with_strike

import pytest

from app.badge.factories import BadgeFactory
from app.badge.factories.user_badge_factory import UserBadgeFactory
from app.common.enums import Groups
from app.content.factories.user_factory import UserFactory
from app.util.test_utils import add_user_to_group_with_name
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


@pytest.mark.django_db
def test_completion_percentage_excludes_all_unregistered_users(badge, api_client):
    """Unregistered users are all users who do not have a membership in the TIHLDE group
    When calculating completing percentage, only members in this group are counted.
    Creates 4 valid users plus one unregistered user. Result should be 25 == 1/4 * 100"""

    member_with_badge = UserFactory()

    add_user_to_group_with_name(UserFactory(), Groups.TIHLDE)
    add_user_to_group_with_name(UserFactory(), Groups.TIHLDE)
    add_user_to_group_with_name(UserFactory(), Groups.TIHLDE)
    add_user_to_group_with_name(member_with_badge, Groups.TIHLDE)

    UserBadgeFactory(badge=badge, user=member_with_badge)
    member_client = api_client(member_with_badge)

    UserFactory()

    url = _get_badges_url()

    response = member_client.get(url)
    response = response.json()

    assert response.get("results")[0].get("total_completion_percentage") == 25.0
