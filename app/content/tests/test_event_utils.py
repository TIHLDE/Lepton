from datetime import timedelta

import pytest

from app.content.factories import EventFactory, RegistrationFactory
from app.content.util.event_utils import get_countdown_time
from app.payment.factories import PaidEventFactory


@pytest.fixture()
def paid_event():
    return PaidEventFactory()


@pytest.fixture()
def event():
    return EventFactory()


@pytest.fixture()
def registration(paid_event):
    return RegistrationFactory(event=paid_event)


@pytest.mark.django_db
def test_that_paytime_countdown_adds_ten_minutes(paid_event):
    """
    Should return the countdown time of the event + 10 minutes.
    """

    paytime = paid_event.paytime
    paytime_in_seconds = (paytime.hour * 60 + paytime.minute) * 60 + paytime.second

    countdown_time = get_countdown_time(paid_event.event)

    ten_minutes = timedelta(minutes=10)
    ten_minutes_in_seconds = ten_minutes.seconds

    assert countdown_time - paytime_in_seconds == ten_minutes_in_seconds
