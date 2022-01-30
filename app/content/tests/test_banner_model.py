from datetime import datetime
from unittest import mock

import pytest

from app.content.factories.banner_factory import BannerFactory


@pytest.mark.django_db
@mock.patch("app.content.models.banner.now")
@pytest.mark.parametrize(
    "visible_until, now, expected_value",
    [
        (None, datetime(2022, 1, 1, 0), False),
        (None, datetime(2022, 1, 1, 1), True),
        (None, datetime(2022, 1, 1, 2), True),
        (datetime(2022, 1, 1, 3), datetime(2022, 1, 1, 0), False),
        (datetime(2022, 1, 1, 3), datetime(2022, 1, 1, 1), True),
        (datetime(2022, 1, 1, 3), datetime(2022, 1, 1, 2), True),
        (datetime(2022, 1, 1, 3), datetime(2022, 1, 1, 3), True),
        (datetime(2022, 1, 1, 3), datetime(2022, 1, 1, 4), False),
    ],
)
def test_banner_is_visible(mock_now, visible_until, now, expected_value):
    "Banner is be visible when visible_from is passed and visible_until is not passed or None"
    banner = BannerFactory(
        visible_from=datetime(2022, 1, 1, 1), visible_until=visible_until
    )

    mock_now.return_value = now
    is_visible = banner.is_visible

    assert is_visible == expected_value
