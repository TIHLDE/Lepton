from datetime import datetime, timedelta
from unittest import mock

import pytest

from app.content.factories import StrikeFactory
from app.util.utils import getTimezone


@pytest.mark.django_db
@mock.patch("app.content.models.strike.now")
@pytest.mark.parametrize(
    ("today", "created_at", "expected_result"),
    [
        (datetime(2021, 11, 29, 2), datetime(2021, 11, 9), False),
        (datetime(2021, 11, 29), datetime(2021, 11, 9), True),
        (datetime(2021, 12, 5), datetime(2021, 11, 9, 2), True),
        (datetime(2022, 1, 1), datetime(2021, 11, 9, 2), True),
        (datetime(2025, 1, 1), datetime(2021, 11, 9, 2), False),
        (datetime(2022, 1, 10), datetime(2021, 11, 9, 2), True),
        (datetime(2022, 1, 10, 4), datetime(2021, 11, 9, 2), False),
        (datetime(2022, 1, 30, 1), datetime(2022, 1, 9), False),
        (datetime(2022, 1, 29), datetime(2022, 1, 9), True),
        (datetime(2022, 1, 30), datetime(2021, 12, 7), True),
        (datetime(2022, 1, 30, 1), datetime(2021, 12, 7), False),
    ],
)
def test_strike_is_active_or_not_with_freeze_through_winter_holiday(
    mock_now, today, created_at, expected_result
):
    """Strikes are frozen in winter from the 29th of November to the 1st of January."""
    today = today.replace(tzinfo=getTimezone())
    created_at = created_at.replace(tzinfo=getTimezone())

    mock_now.return_value = today
    strike = StrikeFactory.build(created_at=created_at)

    assert strike.active == expected_result


@pytest.mark.django_db
@mock.patch("app.content.models.strike.now")
@pytest.mark.parametrize(
    ("today", "created_at", "expected_result"),
    [
        (datetime(2021, 9, 4, 1), datetime(2021, 5, 9, 22), True),
        (datetime(2021, 9, 4, 1), datetime(2021, 5, 9), False),
        (datetime(2021, 5, 9, 23), datetime(2021, 4, 20), True),
        (datetime(2021, 5, 10, 1), datetime(2021, 4, 20), False),
        (datetime(2021, 5, 10, 1), datetime(2021, 4, 20, 1), True),
        (datetime(2021, 7, 20), datetime(2021, 4, 20, 1), True),
        (datetime(2021, 5, 9), datetime(2021, 4, 19), True),
        (datetime(2021, 8, 16), datetime(2021, 4, 20, 1), True),
        (datetime(2021, 8, 16, 2), datetime(2021, 4, 20, 1), False),
        (datetime(2021, 9, 5), datetime(2021, 7, 10), True),
        (datetime(2021, 9, 5, 1), datetime(2021, 7, 10), False),
        (datetime(2021, 9, 25, 1), datetime(2021, 9, 5), False),
        (datetime(2021, 9, 25), datetime(2021, 9, 5), True),
    ],
)
def test_strike_is_active_or_not_with_freeze_through_summer_holiday(
    mock_now, today, created_at, expected_result
):
    """Strikes are frozen in summer from the 10th of May to 15th of August."""
    today = today.replace(tzinfo=getTimezone())
    created_at = created_at.replace(tzinfo=getTimezone())

    mock_now.return_value = today
    strike = StrikeFactory.build(created_at=created_at)

    assert strike.active == expected_result


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("created_at", "days_active"),
    [
        (datetime(2021, 3, 1), 20),
        (datetime(2021, 3, 1, 1), 20),
        (datetime(2021, 5, 9), 118),
        (datetime(2021, 5, 9, 4), 118),
        (datetime(2021, 5, 3), 118),
        (datetime(2021, 8, 14), 22),
        (datetime(2021, 11, 9), 20),
        (datetime(2021, 11, 9, 1), 62),
        (datetime(2021, 12, 24), 37),
    ],
)
def test_active_days_of_a_strike_with_freeze_through_holidays(created_at, days_active):
    """Days active is the amount of days a strike is active which is at least 20 days"""
    created_at = created_at.replace(tzinfo=getTimezone())

    strike = StrikeFactory.build(created_at=created_at)

    active_days = strike.expires_at - strike.created_at

    assert active_days == timedelta(days_active)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("created_at", "is_different_year"),
    [
        (datetime(2021, 1, 1), True),
        (datetime(2021, 5, 9), True),
        (datetime(2021, 11, 8, 23, 59), True),
        (datetime(2021, 11, 9), True),
        (datetime(2021, 11, 9, 0, 0, 1), False),
        (datetime(2021, 11, 30), False),
        (datetime(2021, 12, 31, 23, 59), False),
        (datetime(2022, 1, 1), True),
    ],
)
def test_year_of_expire_date_different_than_created_year_with_freeze_through_winter_holidays(
    created_at, is_different_year
):
    """A strike should have a different year of expired date
    if created less 20 days before the winter holiday"""
    created_at = created_at.replace(tzinfo=getTimezone())

    strike = StrikeFactory.build(created_at=created_at)

    created_year = strike.created_at.year
    expired_year = strike.expires_at.year

    assert (expired_year == created_year) == is_different_year
