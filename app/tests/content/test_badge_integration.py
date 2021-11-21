import uuid
from datetime import timedelta

from rest_framework import status

import pytest

from app.common.enums import AdminGroup, Groups
from app.content.factories.badge_factory import BadgeFactory
from app.util.test_utils import get_api_client
from app.util.utils import now

API_BADGE_BASE_URL = "/badges/"


def _get_badge_leaderboard_url():
    return f"{API_BADGE_BASE_URL}leaderboard/"


def _get_badge_specific_leaderboard_url(badge):
    return f"{API_BADGE_BASE_URL}{badge.id}/leaderboard/"


def _get_user_badge_url(badge):
    return f"{API_BADGE_BASE_URL}{badge.id}/users/"


def _get_user_data(user):
    return {"user": {"user_id": user.user_id}}


@pytest.mark.django_db
def test_get_badge_leaderboard_as_anonymous_user(default_client):
    """An anonymous user should not be able to see the leaderboard"""

    url = _get_badge_leaderboard_url()
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_badge_spesific_leaderboard_as_anonymous_user(default_client, badge):
    """An anonymous user should not be able to see badge specific leaderboard"""

    url = _get_badge_specific_leaderboard_url(badge)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_get_request_for_user_badges_as_anonymous_user(default_client, badge):
    """An anonymous user should not be able to do a post request for a user badge"""

    url = _get_user_badge_url(badge)
    response = default_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_403_FORBIDDEN),
        (AdminGroup.INDEX, status.HTTP_405_METHOD_NOT_ALLOWED),
        (AdminGroup.NOK, status.HTTP_403_FORBIDDEN),
        (AdminGroup.SOSIALEN, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
        (Groups.TIHLDE, status.HTTP_403_FORBIDDEN),
    ],
)
def test_get_request_for_user_badges_as_different_groups(
    user, badge, group_name, expected_status_code
):
    """Only Index has read access, but get request is not an allowed method anyway"""

    url = _get_user_badge_url(badge)
    client = get_api_client(user=user, group_name=group_name)
    response = client.get(url)

    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_create_user_badge_for_user_badges_as_member(member, badge):
    """All members should be able to create a user badge"""

    url = _get_user_badge_url(badge)
    client = get_api_client(user=member)
    data = _get_user_data(member)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_user_badge_for_already_existing_user_badges(member, badge):
    """User badges that already exist can not be created and returns a 400 Bad Request with detail"""

    url = _get_user_badge_url(badge)
    client = get_api_client(user=member)
    data = _get_user_data(member)
    client.post(url, data)
    response = client.post(url, data)
    detail = response.json().get("detail")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert detail == "Denne badgen er allerede fullført"


@pytest.mark.django_db
def test_create_user_badge_for_non_existent_user(member, badge):
    """User has to exist for a User Badge to be created. Therefore the view returns a 404 with detail"""

    url = _get_user_badge_url(badge)
    client = get_api_client(user=member)
    data = {"user": {"user_id": "non_existent_user_id"}}
    response = client.post(url, data)
    detail = response.json().get("detail")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert detail == "Kunne ikke finne brukeren"


@pytest.mark.django_db
def test_create_user_badge_for_non_existent_badge(member):
    """Badge has to exist for a User Badge to be created. Therefore the view returns a 404 with detail"""

    url = f"{API_BADGE_BASE_URL}{uuid.uuid4}/users/"
    client = get_api_client(user=member)
    data = _get_user_data(member)
    response = client.post(url, data)
    detail = response.json().get("detail")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert detail == "Badgen kunne ikke bli opprettet"


@pytest.mark.django_db
def test_create_user_badge_for_badge_active_from_tomorrow(member):
    """Badge has to be active for a User Badge to be created. Therefore the view returns a 400 with detail.
        active_from is set to tomorrow and active_to is not defined so badge is only active from tomorrow and on"""

    badge = BadgeFactory(active_from=now() + timedelta(1))

    url = _get_user_badge_url(badge)
    client = get_api_client(user=member)
    data = _get_user_data(member)
    response = client.post(url, data)
    detail = response.json().get("detail")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert detail == "Badgen er ikke aktiv"


@pytest.mark.django_db
def test_create_user_badge_for_badge_active_until_yesterday(member):
    """Badge has to be active for a User Badge to be created. Therefore the view returns a 400 with detail.
        active_from is not defined and active_to is set to yesterday so badge is only active until yesterday"""

    badge = BadgeFactory(active_to=now() - timedelta(1))

    url = _get_user_badge_url(badge)
    client = get_api_client(user=member)
    data = _get_user_data(member)
    response = client.post(url, data)
    detail = response.json().get("detail")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert detail == "Badgen er ikke aktiv"


@pytest.mark.django_db
def test_create_user_badge_for_badge_active_in_future_period(member):
    """Badge has to be active for a User Badge to be created. Therefore the view returns a 400 with detail.
        active_from is set to tomorrow and active_to is set to two days in the future so badge is only active from tomorrow and on"""

    badge = BadgeFactory(
        active_from=now() + timedelta(1), active_to=now() + timedelta(2)
    )

    url = _get_user_badge_url(badge)
    client = get_api_client(user=member)
    data = _get_user_data(member)
    response = client.post(url, data)
    detail = response.json().get("detail")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert detail == "Badgen er ikke aktiv"


@pytest.mark.django_db
def test_create_user_badge_for_badge_active_in_previous_period(member):
    """Badge has to be active for a User Badge to be created. Therefore the view returns a 400 with detail.
        active_from is set to two days ago and active_to is set to yesterday so badge was only active until yesterday"""

    badge = BadgeFactory(
        active_from=now() - timedelta(2), active_to=now() - timedelta(1)
    )

    url = _get_user_badge_url(badge)
    client = get_api_client(user=member)
    data = _get_user_data(member)
    response = client.post(url, data)
    detail = response.json().get("detail")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert detail == "Badgen er ikke aktiv"


@pytest.mark.django_db
def test_create_user_badge_for_badge_with_active_to_before_active_from(member):
    """Badge has to be active for a User Badge to be created. Therefore the view returns a 400 with detail.
        active_from is set to yesterday and active_to is set to two days ago so badge is never active"""

    badge = BadgeFactory(
        active_from=now() - timedelta(1), active_to=now() - timedelta(2)
    )

    url = _get_user_badge_url(badge)
    client = get_api_client(user=member)
    data = _get_user_data(member)
    response = client.post(url, data)
    detail = response.json().get("detail")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert detail == "Badgen er ikke aktiv"


@pytest.mark.django_db
def test_create_user_badge_for_badge_active_in_current_period(member):
    """Badge has to be active for a User Badge to be created. Therefore the view returns a 200.
        active_from is set to yesterday and active_to is set to tomorrow so badge is active from yesterday to tomorrow"""

    badge = BadgeFactory(
        active_from=now() - timedelta(1), active_to=now() + timedelta(1)
    )

    url = _get_user_badge_url(badge)
    client = get_api_client(user=member)
    data = _get_user_data(member)
    response = client.post(url, data)

    assert response.status_code == status.HTTP_200_OK
