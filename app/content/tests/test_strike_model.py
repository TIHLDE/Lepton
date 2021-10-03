from datetime import datetime
from unittest import mock

import pytest

from app.content.factories.strike_factory import StrikeFactory
from app.content.models.strike import Strike

pytestmark = pytest.mark.django_db


@mock.patch("app.content.models.strike.today")
def test_strike_freezer(mock_today):

    # Arrange
    mock_today.return_value = datetime(2021, 6, 1)
    StrikeFactory()
    strike = Strike(created_at=datetime(2021, 5, 31))

    # Act and Assert
    assert strike.active
