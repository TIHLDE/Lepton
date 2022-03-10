from datetime import timedelta

import pytest

from app.communication.factories.banner_factory import BannerFactory
from app.util.utils import now


@pytest.mark.django_db
@pytest.mark.parametrize(
    "visible_from, visible_until, expected_value",
    [
        (now() + timedelta(hours=1), now() + timedelta(hours=2), False),
        (now(), now() + timedelta(2), True),
        (now() - timedelta(hours=1), now() + timedelta(hours=1), True),
        (now() - timedelta(hours=2), now() - timedelta(hours=1), False),
    ],
)
def test_banner_is_visible_with_different_dates(
    visible_from, visible_until, expected_value
):
    "Banner is be visible when visible_from is passed and visible_until is not passed or None"
    banner = BannerFactory(visible_from=visible_from, visible_until=visible_until)

    is_visible = banner.is_visible

    assert is_visible == expected_value


@pytest.mark.django_db
def test_two_banners_can_not_be_visible_simultaneously():
    "A banner can not be visible in the same timeframe as another badge"
    BannerFactory()

    with pytest.raises(ValueError) as v_err:
        BannerFactory()

    assert "Det finnes allerede et banner som er synlig" == str(v_err.value)


@pytest.mark.django_db
def test_banner_valid_until_date_before_valid_from():
    "A banner's valid until date can not be before valid until date"

    with pytest.raises(ValueError) as v_err:
        BannerFactory(visible_from=now() + timedelta(1), visible_until=now())

    assert "Datoer er satt feil" == str(v_err.value)
