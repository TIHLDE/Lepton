from datetime import timedelta

import pytest

from app.content.factories.badge_factory import BadgeFactory
from app.util.utils import now


@pytest.mark.django_db
def test_badge_not_active_when_badge_is_active_from_tomorrow():
    """Badge should not be active when active_from is set to
        tomorrow and active_to is undefined"""

    badge = BadgeFactory(active_from=now() + timedelta(1))

    assert not badge.active


@pytest.mark.django_db
def test_badge_not_active_when_badge_is_active_to_yesterday():
    """Badge should not be active when active_from is
        undefined and active_to is set to yesterday"""

    badge = BadgeFactory(active_to=now() - timedelta(1))

    assert not badge.active


@pytest.mark.django_db
def test_badge_not_active_when_badge_is_active_in_future_period():
    """Badge should not be active when active_from is set to
        tomorrow and active_to is set to two days from now"""

    badge = BadgeFactory(
        active_from=now() + timedelta(1), active_to=now() + timedelta(2)
    )

    assert not badge.active


@pytest.mark.django_db
def test_badge_not_active_when_badge_is_active_in_previous_period():
    """Badge should not be active when active_from is set to
        two days ago and active_to is set to yesterday"""

    badge = BadgeFactory(
        active_from=now() - timedelta(2), active_to=now() - timedelta(1)
    )

    assert not badge.active


@pytest.mark.django_db
def test_badge_not_active_when_active_from_is_after_active_to():
    """Badge should never be active when active_from is set to
        after active_to"""

    badge = BadgeFactory(
        active_from=now() - timedelta(1), active_to=now() - timedelta(2)
    )

    assert not badge.active


@pytest.mark.django_db
def test_badge_active_when_active_from_now_to_minute_later():
    """Badge should be active when active_from is set to
        now and active_to is set to a minute from now"""

    badge = BadgeFactory(active_from=now(), active_to=now() + timedelta(minutes=1))

    assert badge.active


@pytest.mark.django_db
def test_if_badge_with_active_to_set_to_later_is_not_public():
    """When badge has only active_to set and badge is active,
        it is not public"""

    badge = BadgeFactory(active_to=now() + timedelta(minutes=1))

    assert not badge.is_public


@pytest.mark.django_db
def test_if_badge_with_active_from_set_to_later_is_not_public():
    """When badge has only active_from set and badge is not active,
        it is not public"""

    badge = BadgeFactory(active_from=now() + timedelta(minutes=1))

    assert not badge.is_public
