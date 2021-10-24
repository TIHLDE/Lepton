from datetime import datetime, timedelta
from unittest import mock

import pytest

from app.content.factories.strike_factory import StrikeFactory
from app.content.models.strike import Strike

pytestmark = pytest.mark.django_db


@mock.patch("app.content.models.strike.today")
def test_active_or_not_strike_with_freeze_through_holidays(mock_today):
    '''
    Test that uses a mock function of today() and a specified 
    creation date to check if a strike is active or not on the 
    date made by the mocked today() function. This test can be 
    especially used to check if a strike is active after a holiday

    :mock_today: the mocked today() function\n
    :strike: Strike instance with modified creation date\n
    :assert: weather or not strike is active on specified day\n
    '''

    mock_today.return_value = datetime(2022, 1, 30)
    StrikeFactory()
    strike = Strike(created_at=datetime(2022, 12, 7))


    assert strike.active

def test_active_days_of_a_strike_with_freeze_through_holidays():
    '''
    Test that uses a specified creation date to check 
    how many days a strike has been active for. If 
    creation date is set far from a holiday, active
    days will be 20. To check if strike is active 
    during a holiday, 
    assert active_days > timedelta(days=20)

    :strike: Strike instance with modified creation date\n
    :strike.created_at: date of when strike is created\n
    :strike.expires_at: date of when strike is expired\n
    :active_days: difference between expried and created date\n
    :assert: weather or not number of active days of strike is equal to number of days\n
    '''

    StrikeFactory()
    strike = Strike(created_at=datetime(2021, 5, 1))

    active_days = strike.expires_at - strike.created_at

    assert active_days == timedelta(days=118)

def test_year_of_expire_date_different_than_created_year_with_freeze_through_holidays():
    '''
    Test that checks if start of expired date of strike
    is a different year than year when strike is created. 
    For example a strike created in desember will have 
    an expired date the next year

    :strike: Strike instance with modified creation date\n
    :created_year: year of when strike is created\n
    :expired_year: year of when strike is expired\n
    :assert: weather or not expired_year is one year after created_year\n
    '''

    StrikeFactory()
    strike = Strike(created_at=datetime(2021, 11, 30))

    created_year = strike.created_at.year
    expired_year = strike.expires_at.year

    assert  expired_year == created_year + 1
