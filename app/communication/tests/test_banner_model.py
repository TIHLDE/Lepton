from datetime import datetime, timedelta

import pytest

from app.communication.exceptions import (
    AnotherVisibleBannerError,
    DatesMixedError,
)
from app.communication.factories.banner_factory import BannerFactory
from app.util.utils import get_timezone, now


@pytest.mark.parametrize(
    "visible_from_delta, visible_until_delta",
    [
        (5, 5),
        (5, -5),
        (-5, 5),
        (-5, -5),
    ],
)
@pytest.mark.django_db
def test_two_banners_can_not_be_visible_simultaneously_in_any_period(
    visible_from_delta, visible_until_delta
):
    """A banner can not be visible in the same timeframe as another badge
    This test uses timedelta and parameterize to switch visible_from
    and visible_until between 5 days earlier or later."""
    existing_banner = BannerFactory(
        visible_from=datetime(2020, 1, 1, tzinfo=get_timezone()),
        visible_until=datetime(2021, 1, 1, tzinfo=get_timezone()),
    )

    with pytest.raises(AnotherVisibleBannerError):
        BannerFactory(
            visible_from=existing_banner.visible_from + timedelta(visible_from_delta),
            visible_until=existing_banner.visible_until
            + timedelta(visible_until_delta),
        )


@pytest.mark.django_db
def test_banner_valid_until_date_before_valid_from():
    "A banner's valid until date can not be before valid until date"

    with pytest.raises(DatesMixedError):
        BannerFactory(visible_from=now() + timedelta(1), visible_until=now())
