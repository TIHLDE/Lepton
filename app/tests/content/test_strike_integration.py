from datetime import timedelta

from rest_framework import status

import pytest

from app.common.enums import AdminGroup, Groups
from app.common.enums import NativeStrikeEnum as StrikeEnum
from app.content.factories import StrikeFactory
from app.content.factories.event_factory import EventFactory
from app.content.factories.user_factory import UserFactory
from app.util.test_utils import get_api_client
from app.util.utils import now

API_STRIKE_BASE_URL = "/strikes/"


@pytest.fixture()
def strike_post_data():
    return {
        "user_id": UserFactory().user_id,
        "event": EventFactory().id,
        "description": "Strike test description",
        "strike_size": 1,
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK),
        (AdminGroup.NOK, status.HTTP_200_OK),
        (AdminGroup.SOSIALEN, status.HTTP_200_OK),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
        (Groups.TIHLDE, status.HTTP_403_FORBIDDEN),
    ],
)
def test_list_strikes_as_member_of_board_or_sub_group(
    member, group_name, expected_status_code
):
    """A member of HS, Index, NOK or Sosialen can list strikes"""
    client = get_api_client(user=member, group_name=group_name)
    response = client.get(API_STRIKE_BASE_URL)

    assert response.status_code == expected_status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK),
        (AdminGroup.NOK, status.HTTP_200_OK),
        (AdminGroup.SOSIALEN, status.HTTP_200_OK),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
        (Groups.TIHLDE, status.HTTP_403_FORBIDDEN),
    ],
)
def test_create_strikes_as_member_of_board_or_sub_group(
    member, group_name, expected_status_code, strike_post_data
):
    """A member of HS, Index, NOK or Sosialen can create a strike"""
    client = get_api_client(user=member, group_name=group_name)
    response = client.post(API_STRIKE_BASE_URL, strike_post_data)

    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_only_active_strikes_are_listed(admin_user):
    """Out of 2 strikes created, only the active strike is shown"""
    client = get_api_client(user=admin_user)

    StrikeFactory.build(created_at=now() - timedelta(days=365))
    StrikeFactory()

    response = client.get(API_STRIKE_BASE_URL)
    response = response.json()

    assert response["count"] == 1


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("strike_enum", "expected_status_code"),
    [
        (StrikeEnum.BAD_BEHAVIOR, status.HTTP_200_OK),
        (StrikeEnum.EVAL_FORM, status.HTTP_200_OK),
        (StrikeEnum.LATE, status.HTTP_200_OK),
        (StrikeEnum.NO_SHOW, status.HTTP_200_OK),
        (StrikeEnum.PAST_DEADLINE, status.HTTP_200_OK),
        ("NOT A VALID ENUM", status.HTTP_404_NOT_FOUND),
    ],
)
def test_all_strike_enums_are_valid(
    admin_user, strike_enum, expected_status_code, strike_post_data
):
    """If a strike enum is not recognized, a 404 is returned"""
    strike_post_data["enum"] = strike_enum

    client = get_api_client(user=admin_user)
    response = client.post(API_STRIKE_BASE_URL, strike_post_data)

    assert response.status_code == expected_status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK),
        (AdminGroup.NOK, status.HTTP_403_FORBIDDEN),
        (AdminGroup.SOSIALEN, status.HTTP_403_FORBIDDEN),
        (AdminGroup.PROMO, status.HTTP_403_FORBIDDEN),
        (Groups.TIHLDE, status.HTTP_403_FORBIDDEN),
    ],
)
def test_delete_strike_as_member_of_board_or_sub_goup(
    member, group_name, expected_status_code
):
    """A member of HS or Index can delete a strike"""
    strike = StrikeFactory()
    client = get_api_client(user=member, group_name=group_name)
    response = client.delete(API_STRIKE_BASE_URL + str(strike.id) + "/")

    assert response.status_code == expected_status_code
