from datetime import timedelta

import pytest

from app.badge.factories import BadgeFactory
from app.util.utils import now


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("active_from", "active_to", "expected_result"),
    [
        (now() + timedelta(1), None, False),
        (None, now() - timedelta(1), False),
        (now() + timedelta(1), now() + timedelta(2), False),
        (now() - timedelta(2), now() - timedelta(1), False),
        (now() - timedelta(1), now() - timedelta(2), False),
        (now() - timedelta(1), now() + timedelta(1), True),
        (now(), now() + timedelta(hours=1), True),
        (now(), None, True),
        (None, now() + timedelta(1), True),
        (None, None, True),
    ],
)
def test_badge_is_active_with_different_active_dates(
    active_from, active_to, expected_result
):
    """Tests several arguments for active_from and active_to dates and checks whether badge is active
    or not depending on the arguments above. Badge is not active if active_from is later than now
    or active_to is earlier than now. If active_to/from is None, it is treated as infinitly far in
    the past for active_from and in the future for active_to."""

    badge = BadgeFactory(active_to=active_to, active_from=active_from)

    assert badge.is_active is expected_result


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("active_from", "active_to", "expected_result"),
    [
        (now() + timedelta(1), None, False),
        (None, now() - timedelta(1), True),
        (now() + timedelta(1), now() + timedelta(2), False),
        (now() - timedelta(2), now() - timedelta(1), True),
        (now() - timedelta(1), now() - timedelta(2), True),
        (now() - timedelta(1), now() + timedelta(1), False),
        (now(), now() + timedelta(hours=1), False),
        (now(), None, True),
        (None, now() + timedelta(1), False),
        (None, None, True),
    ],
)
def test_badge_is_public_with_different_active_dates(
    active_from, active_to, expected_result
):
    """Tests several arguments for active_from and active_to dates and checks whether badge is public
    or not depending on the arguments above. Badge is public if active_to is passed or if active_to
    is None and badge is active. If active_to/from is None, they are treated as infinitly far in
    the past for active_from and in the future for active_to."""

    badge = BadgeFactory(active_to=active_to, active_from=active_from)

    assert badge.is_public is expected_result
