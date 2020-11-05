from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from django.core.exceptions import ValidationError

import pytest

from ..factories import EventFactory, PriorityFactory, RegistrationFactory


@pytest.fixture()
def event():
    return EventFactory()


@pytest.fixture()
def registration(event):
    return RegistrationFactory(event=event)


@pytest.fixture()
def priority():
    return PriorityFactory()


@pytest.mark.django_db
def test_expired_when_event_has_not_expired(event):
    """Should return False when end date is before yesterday."""
    event.end_date = datetime.now(tz=timezone.utc)

    assert not event.expired


@pytest.mark.django_db
def test_expired_when_event_has_expired(event):
    """Should return True when end date is after yesterday."""
    event.end_date = datetime.now(tz=timezone.utc) - timedelta(days=10)

    assert event.expired


@pytest.mark.django_db
@pytest.mark.parametrize(
    "users_not_on_wait, users_on_wait, expected_list_count",
    [(0, 0, 0), (5, 0, 5), (1, 4, 1),],
)
def test_list_count(event, users_not_on_wait, users_on_wait, expected_list_count):
    """Should return the number of registered users who are to attend."""
    event.limit = users_not_on_wait
    RegistrationFactory.create_batch(users_on_wait, is_on_wait=True, event=event)
    RegistrationFactory.create_batch(users_not_on_wait, is_on_wait=False, event=event)

    assert event.list_count == expected_list_count


@pytest.mark.django_db
@pytest.mark.parametrize(
    "users_not_on_wait, users_on_wait, expected_waiting_list_count",
    [(0, 0, 0), (5, 0, 0), (1, 4, 4),],
)
def test_waiting_list_count(
    event, users_not_on_wait, users_on_wait, expected_waiting_list_count
):
    """Should return the number of registered users who are on the waiting list."""
    event.limit = users_not_on_wait
    RegistrationFactory.create_batch(users_on_wait, is_on_wait=True, event=event)
    RegistrationFactory.create_batch(users_not_on_wait, is_on_wait=False, event=event)

    assert event.waiting_list_count == expected_waiting_list_count


@pytest.mark.django_db
def test_has_waiting_list_when_event_does_not_have_limit(event):
    """Test that an event has a waiting list if the limit is not zero and is not full or has users on wait."""
    event.limit = 0

    assert not event.has_waiting_list()


@pytest.mark.django_db
def test_has_waiting_list_when_event_is_full(event):
    """Test that an event has a waiting list if the event is full."""
    event.limit = 1
    RegistrationFactory.create_batch(2, event=event)

    assert event.has_waiting_list()


@pytest.mark.django_db
def test_has_waiting_list_when_event_has_users_on_wait(event):
    """Test that an event has a waiting list if there are any users on the waiting list."""
    event.limit = 10
    RegistrationFactory(event=event)
    waiting_list_registration = RegistrationFactory(event=event)

    waiting_list_registration.is_on_wait = True
    waiting_list_registration.save()

    assert event.has_waiting_list()


@pytest.mark.django_db
def test_has_waiting_list_when_event_is_not_full(event):
    """
        Test that an event does not have a waiting list when there are available spots and no users on wait.
    """
    event.limit = 100
    RegistrationFactory.create_batch(1, event=event)

    assert not event.has_waiting_list()


@pytest.mark.django_db
@pytest.mark.parametrize("limit, has_limit", [(0, False), (1, True)])
def test_has_limit(event, limit, has_limit):
    """Should return True if limit is zero, else False."""
    event.limit = limit

    assert event.has_limit() == has_limit


@pytest.mark.django_db
@pytest.mark.parametrize(
    "limit, number_of_attendees, is_full", [(1, 1, True), (1, 2, True), (2, 1, False)]
)
def test_is_full(event, limit, number_of_attendees, is_full):
    """
        Should return True if number of registered users is greater than limit, else False.
    """
    event.limit = limit
    RegistrationFactory.create_batch(number_of_attendees, event=event)

    assert event.is_full == is_full


@pytest.mark.django_db
def test_has_priorities_when_no_priorities_exists(event):
    """Should return False if no registration priorities are connected to event."""
    event.registration_priorities.clear()

    assert not event.has_priorities()


@pytest.mark.django_db
def test_has_priorities_when_priorities_exists_on_event(event, priority):
    """Should return True if any registration priorities are connected to event."""
    event.registration_priorities.add(priority)

    assert event.has_priorities()


@pytest.mark.django_db
@patch("app.content.models.event.Event.validate_start_end_registration_times")
def test_clean_validates_date_times(mock_validate_start_end_registration_times, event):
    """Test that the clean method initiates validation sequence."""
    event.clean()

    assert mock_validate_start_end_registration_times.called


@pytest.mark.django_db
@pytest.mark.parametrize(
    "start_registration_at, end_registration_at",
    [(None, datetime.now()), (datetime.now(), None), (datetime.now(), datetime.now())],
)
def test_check_sign_up_and_registration_times_when_event_does_not_have_sign_up_raises_error(
    event, start_registration_at, end_registration_at
):
    """Should raise ValidationError if event does not have sign up and dates are set."""
    event.sign_up = False
    event.start_registration_at = start_registration_at
    event.end_registration_at = end_registration_at

    with pytest.raises(ValidationError):
        event.check_sign_up_and_registration_times()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "start_registration_at, end_registration_at, sign_off_deadline",
    [
        (None, None, None),
        (None, None, datetime.now()),
        (None, datetime.now(), datetime.now()),
        (datetime.now(), None, None),
        (datetime.now(), None, datetime.now()),
        (datetime.now(), datetime.now(), None),
    ],
)
def test_check_if_registration_is_not_set_when_event_has_signup_raises_error(
    event, start_registration_at, end_registration_at, sign_off_deadline
):
    """Should raise ValidationError if event has sign up but not required dates."""
    event.sign_up = True
    event.start_registration_at = start_registration_at
    event.end_registration_at = end_registration_at
    event.sign_off_deadline = sign_off_deadline

    with pytest.raises(ValidationError):
        event.check_if_registration_is_not_set()


@pytest.mark.django_db
def test_check_sign_up_and_sign_off_deadline_when_no_sign_up_but_sign_off_deadline_is_set_raises_error(
    event,
):
    """Should raise ValidationError if event has sign off dead line but no sign up."""
    event.sign_up = False
    event.sign_off_deadline = datetime.now()

    with pytest.raises(ValidationError):
        event.check_sign_up_and_sign_off_deadline()


@pytest.mark.django_db
def test_check_start_time_is_before_end_registration(event):
    """Should raise ValidationError if event end date is before event start date."""
    event.start_date = datetime.now()
    event.end_registration_at = datetime.now() + timedelta(days=1)

    with pytest.raises(ValidationError):
        event.check_start_time_is_before_end_registration()


@pytest.mark.django_db
def test_check_start_registration_is_before_end_registration(event):
    """Should raise ValidationError if start time for registration is after registration end time."""
    event.start_registration_at = datetime.now()
    event.end_registration_at = datetime.now() - timedelta(days=1)

    with pytest.raises(ValidationError):
        event.check_start_registration_is_before_end_registration()


@pytest.mark.django_db
def test_check_start_registration_is_after_start_time(event):
    """Should raise ValidationError if registration start time is after event start time."""
    event.start_date = datetime.now()
    event.start_registration_at = datetime.now() + timedelta(days=1)

    with pytest.raises(ValidationError):
        event.check_start_registration_is_after_start_time()


@pytest.mark.django_db
def test_check_end_time_is_before_end_registration(event):
    """Should raise ValidationError if registration end time is after event end time."""
    event.end_date = datetime.now()
    event.end_registration_at = datetime.now() + timedelta(days=1)

    with pytest.raises(ValidationError):
        event.check_end_time_is_before_end_registration()


@pytest.mark.django_db
def test_check_start_date_is_before_deadline(event):
    """Should raise ValidationError if sign off deadline is after event start time."""
    event.start_date = datetime.now()
    event.sign_off_deadline = datetime.now() + timedelta(days=1)

    with pytest.raises(ValidationError):
        event.check_start_date_is_before_deadline()


@pytest.mark.django_db
def test_check_start_registration_is_after_deadline(event):
    """Should raise ValidationError if sign off deadline is after registration start time."""
    event.sign_off_deadline = datetime.now()
    event.start_registration_at = datetime.now() + timedelta(days=1)

    with pytest.raises(ValidationError):
        event.check_start_registration_is_after_deadline()
