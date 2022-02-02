from datetime import timedelta

import pytest

from app.communication.factories.banner_factory import BannerFactory
from app.util.utils import now


@pytest.mark.django_db
@pytest.mark.parametrize(
    "visible_from, visible_until, expected_value",
    [
        (now() - timedelta(hours=1), None, True),
        (now(), None, True),
        (now() + timedelta(hours=1), None, False),
        (now() + timedelta(hours=1), now() + timedelta(hours=2), False),
        (now(), now() + timedelta(2), True),
        (now() - timedelta(hours=1), now() + timedelta(hours=1), True),
        (now() - timedelta(hours=2), now() - timedelta(hours=1), False),
        (now() - timedelta(hours=1), now() - timedelta(hours=2), False),
    ],
)
def test_banner_is_visible_with_different_dates(
    visible_from, visible_until, expected_value
):
    "Banner is be visible when visible_from is passed and visible_until is not passed or None"
    banner = BannerFactory(visible_from=visible_from, visible_until=visible_until)

    is_visible = banner.is_visible

    assert is_visible == expected_value
