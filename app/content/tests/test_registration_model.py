from unittest.mock import patch

from django.core.exceptions import ValidationError

import pytest

from app.common.enums import UserClass, UserStudy
from app.content.factories import (
    EventFactory,
    PriorityFactory,
    RegistrationFactory,
    UserFactory,
)
from app.forms.enums import EventFormType
from app.forms.models.forms import Submission
from app.forms.tests.form_factories import EventFormFactory, SubmissionFactory


@pytest.fixture()
def non_priority_user_class():
    return UserClass.FIRST


@pytest.fixture()
def non_priority_user_study():
    return UserStudy.DATAING


@pytest.fixture()
def user():
    return UserFactory()


@pytest.fixture()
def priority_user_class():
    return UserClass.THIRD


@pytest.fixture()
def priority_user_study():
    return UserStudy.DATAING


@pytest.fixture()
def user_in_priority_pool(priority_user_class, priority_user_study):
    return UserFactory(
        user_class=priority_user_class.value, user_study=priority_user_study.value
    )


@pytest.fixture()
def user_not_in_priority_pool(non_priority_user_class, non_priority_user_study):
    return UserFactory(
        user_class=non_priority_user_class.value,
        user_study=non_priority_user_study.value,
    )


@pytest.fixture()
def priority(priority_user_class, priority_user_study):
    return PriorityFactory(
        user_class=priority_user_class, user_study=priority_user_study
    )


@pytest.fixture()
def event(priority):
    event = EventFactory(limit=1)
    event.registration_priorities.add(priority)
    return event


@pytest.fixture(autouse=True)
def event_with_registrations_and_priority(priority):
    event = EventFactory(limit=1)
    event.registration_priorities.add(priority)
    return event


@pytest.fixture(autouse=True)
def registration_not_in_priority_pool(
    event_with_registrations_and_priority, user_not_in_priority_pool
):
    return RegistrationFactory(
        event=event_with_registrations_and_priority, user=user_not_in_priority_pool
    )


@pytest.fixture(autouse=True)
def registration_in_priority_pool(
    event_with_registrations_and_priority, user_in_priority_pool
):
    return RegistrationFactory(
        event=event_with_registrations_and_priority, user=user_in_priority_pool
    )


@pytest.mark.django_db
def test_swap_users_when_event_is_full(
    event, registration_not_in_priority_pool, user_in_priority_pool
):
    """Test that a prioritized user is swapped with a non prioritized user if the event is full."""

    registration_in_priority_pool = RegistrationFactory(
        event=event, user=user_in_priority_pool
    )

    assert not registration_in_priority_pool.is_on_wait
    assert registration_not_in_priority_pool.is_on_wait


@pytest.mark.django_db
def test_bump_user_when_event_is_not_full(
    event, user_not_in_priority_pool, user_in_priority_pool,
):
    """
    Test that a non prioritized user is not swapped with
    a prioritized user if the event is not full.
    """
    event.limit = 10

    registration_not_in_priority_pool = RegistrationFactory(
        event=event, user=user_not_in_priority_pool
    )
    registration_in_priority_pool = RegistrationFactory(
        event=event, user=user_in_priority_pool
    )

    assert not registration_in_priority_pool.is_on_wait
    assert not registration_not_in_priority_pool.is_on_wait


@pytest.mark.django_db
def test_bump_user_when_user_is_not_in_priority_pool_and_event_is_full(
    event, user_not_in_priority_pool
):
    """Test that users are not swapped when new user is not prioritized and event is full."""
    registration_not_in_priority_pool = RegistrationFactory(
        event=event, user=user_not_in_priority_pool
    )
    other_user_not_in_priority_pool = UserFactory(
        user_class=user_not_in_priority_pool.user_class,
        user_study=user_not_in_priority_pool.user_study,
    )
    other_registration_not_in_priority_pool = RegistrationFactory(
        event=event, user=other_user_not_in_priority_pool
    )

    assert not registration_not_in_priority_pool.is_on_wait
    assert other_registration_not_in_priority_pool.is_on_wait


@pytest.mark.django_db
def test_bump_user_without_event_priorities():
    """Test that users are not swapped when event does not have any priorities."""
    event = EventFactory(limit=1)

    registration_not_on_waiting_list = RegistrationFactory(
        event=event, user=UserFactory()
    )
    registration_on_waiting_list = RegistrationFactory(event=event, user=UserFactory())

    assert not registration_not_on_waiting_list.is_on_wait
    assert registration_on_waiting_list.is_on_wait


@pytest.mark.django_db
def test_that_bump_user_registers_on_waiting_list_when_no_one_to_swap_with_and_event_is_full(
    event_with_registrations_and_priority,
    user_in_priority_pool,
    registration_in_priority_pool,
):
    """
    Test that a prioritized user is put on waiting list
    if there is no one to swap places with and the event is full.
    """
    other_user_in_priority_pool = UserFactory(
        user_class=user_in_priority_pool.user_class,
        user_study=user_in_priority_pool.user_study,
    )
    other_registration_in_priority_pool = RegistrationFactory(
        event=event_with_registrations_and_priority, user=other_user_in_priority_pool
    )

    assert not registration_in_priority_pool.is_on_wait
    assert other_registration_in_priority_pool.is_on_wait


@pytest.mark.django_db
def test_swap_places_with_swaps_users(
    registration_in_priority_pool, registration_not_in_priority_pool
):
    """Should swap is_on_wait values for both users."""
    registration_in_priority_pool.swap_places_with(registration_not_in_priority_pool)

    assert not registration_in_priority_pool.is_on_wait
    assert registration_not_in_priority_pool.is_on_wait


@pytest.mark.django_db
def test_is_prioritized_when_user_in_priority_pool(registration_in_priority_pool):
    """Should return True when user is in a priority pool."""

    assert registration_in_priority_pool.is_prioritized


@pytest.mark.django_db
def test_is_prioritized_when_user_not_in_priority_pool(
    registration_not_in_priority_pool,
):
    """Should return False when user is not in a priority pool."""

    assert not registration_not_in_priority_pool.is_prioritized


@pytest.mark.django_db
@patch("app.content.models.registration.Registration.send_notification_and_mail")
def test_create_calls_send_notification_and_email(
    mock_send_notification_and_mail, event
):
    """send_notification_and_email should be called once during creation."""
    RegistrationFactory(event=event, user=UserFactory())

    assert mock_send_notification_and_mail.called_once


@pytest.mark.django_db
def test_create_when_event_has_waiting_list(event_with_registrations_and_priority):
    """Should put user on waiting list if the event has a waiting list."""
    assert event_with_registrations_and_priority.has_waiting_list()

    new_registration = RegistrationFactory(
        event=event_with_registrations_and_priority, user=UserFactory()
    )

    assert new_registration.is_on_wait


@pytest.mark.django_db
def test_users_are_not_swapped_when_both_are_in_a_priority_pool(
    event_with_registrations_and_priority,
    registration_in_priority_pool,
    priority_user_class,
    priority_user_study,
):
    """Should not swap users if both are in a priority pool."""
    user_in_priority_pool = UserFactory(
        user_class=priority_user_class.value, user_study=priority_user_study.value
    )
    other_registration_in_priority_pool = RegistrationFactory(
        event=event_with_registrations_and_priority, user=user_in_priority_pool
    )

    assert not registration_in_priority_pool.is_on_wait
    assert other_registration_in_priority_pool.is_on_wait


@pytest.mark.django_db
def test_registration_in_queue_is_deleted_priority_in_waiting_list_is_moved_to_queue(
    event_with_registrations_and_priority,
    registration_in_priority_pool,
    priority_user_class,
    priority_user_study,
    non_priority_user_study,
):
    """Swap registration when user is deleted with prioritized user."""
    user_in_priority_pool = UserFactory(
        user_class=priority_user_class.value, user_study=priority_user_study.value
    )
    other_registration_in_priority_pool = RegistrationFactory(
        event=event_with_registrations_and_priority, user=user_in_priority_pool
    )
    user_not_in_priority_pool = UserFactory(
        user_class=priority_user_class.value, user_study=non_priority_user_study.value
    )
    registration_not_in_priority_pool = RegistrationFactory(
        event=event_with_registrations_and_priority, user=user_not_in_priority_pool
    )

    registration_in_priority_pool.delete()
    other_registration_in_priority_pool.refresh_from_db()
    registration_not_in_priority_pool.refresh_from_db()

    assert not registration_in_priority_pool.event.registrations.filter(
        registration_id=registration_in_priority_pool.registration_id
    ).exists()
    assert not other_registration_in_priority_pool.is_on_wait
    assert registration_not_in_priority_pool.is_on_wait


@pytest.mark.django_db
def test_registration_in_queue_is_deleted_if_no_priority_registration_in_waiting_list_first_registration_is_moved_to_queue(
    event_with_registrations_and_priority,
    registration_in_priority_pool,
    priority_user_class,
    non_priority_user_study,
):
    """Swap registration when user is deleted with first registration in waiting list, if no priority exists."""
    user_not_in_priority_pool = UserFactory(
        user_class=priority_user_class.value, user_study=non_priority_user_study.value
    )
    registration_not_in_priority_pool = RegistrationFactory(
        event=event_with_registrations_and_priority, user=user_not_in_priority_pool
    )
    other_user_not_in_priority_pool = UserFactory(
        user_class=priority_user_class.value, user_study=non_priority_user_study.value
    )
    other_registration_not_in_priority_pool = RegistrationFactory(
        event=event_with_registrations_and_priority,
        user=other_user_not_in_priority_pool,
    )

    registration_in_priority_pool.delete()
    registration_not_in_priority_pool.refresh_from_db()
    other_registration_not_in_priority_pool.refresh_from_db()

    assert not registration_in_priority_pool.event.registrations.filter(
        registration_id=registration_in_priority_pool.registration_id
    ).exists()
    assert not registration_not_in_priority_pool.is_on_wait
    assert other_registration_not_in_priority_pool.is_on_wait


@pytest.mark.django_db
def test_registration_in_queue_is_deleted_if_no_waiting_list(
    event_with_registrations_and_priority, registration_in_priority_pool,
):
    """Test that if there is no waiting list, a user is still able to unregister from  an event"""
    registration_in_priority_pool.delete()
    event_with_registrations_and_priority.refresh_from_db()

    assert not registration_in_priority_pool.event.registrations.filter(
        registration_id=registration_in_priority_pool.registration_id
    ).exists()
    assert not event_with_registrations_and_priority.get_waiting_list().exists()


@pytest.mark.django_db
def test_delete_registration_when_no_users_on_wait_are_in_a_priority_pool_bumps_first_registration_on_wait():
    """
    Test that the first registration on wait is moved up when
    a registration is deleted and no registered users are prioritized.
    """
    event = EventFactory(limit=1)
    priority = PriorityFactory(user_study=UserStudy.DATAING, user_class=UserClass.FIRST)
    event.registration_priorities.add(priority)

    user_not_in_priority_pool = UserFactory(
        user_study=UserStudy.DIGFOR.value, user_class=UserClass.SECOND.value
    )

    registration_to_delete = RegistrationFactory(event=event)
    registration_on_wait = RegistrationFactory(
        event=event, user=user_not_in_priority_pool
    )

    registration_to_delete.delete()

    registration_on_wait.refresh_from_db()

    assert not registration_on_wait.is_on_wait


@pytest.mark.django_db
@pytest.mark.parametrize(
    "form_type,should_exist",
    [(EventFormType.EVALUATION, True), (EventFormType.SURVEY, False)],
)
def test_deleting_registration_deletes_submission(event, user, form_type, should_exist):
    form = EventFormFactory(event=event, type=form_type)
    submission = SubmissionFactory(form=form, user=user)
    registration = RegistrationFactory(event=event, user=user)

    registration.delete()

    assert Submission.objects.filter(id=submission.id).exists() is should_exist


@pytest.mark.django_db
def test_create_registration_without_submission_answer_fails(event, user):
    EventFormFactory(event=event, type=EventFormType.SURVEY)
    with pytest.raises(ValidationError):
        RegistrationFactory(event=event, user=user)


@pytest.mark.django_db
def test_bump_user_from_wait_when_event_is_full_does_not_increments_limit(
    event_with_registrations_and_priority,
):
    """
    Tests that event limit is not incremented
    when an admin attempts to bump a user up from the wait list when the event is full.
    """
    registration = RegistrationFactory(event=event_with_registrations_and_priority)
    limit = event_with_registrations_and_priority.limit
    registration.is_on_wait = False

    with pytest.raises(ValueError):
        registration.save()

    assert event_with_registrations_and_priority.limit == limit


@pytest.mark.django_db
def test_attempted_bump_user_from_wait_when_event_is_full_does_not_bump_user(
    event_with_registrations_and_priority,
):
    """
    Tests that an admin cannot manualy bump a user up from the wait list when the event is full.
    """
    registration = RegistrationFactory(event=event_with_registrations_and_priority)
    registration.is_on_wait = False

    with pytest.raises(ValueError):
        registration.save()

    registration.refresh_from_db()

    assert registration.is_on_wait


@pytest.mark.django_db
def test_bump_user_from_wait_does_not_increments_limit(
    event_with_registrations_and_priority,
):
    """
    Tests that an admin cannot manualy bump a user up from the wait list when the event is full.
    """
    registration = RegistrationFactory(event=event_with_registrations_and_priority)
    limit = event_with_registrations_and_priority.limit
    registration.is_on_wait = False

    with pytest.raises(ValueError):
        registration.save()

    registration.refresh_from_db()

    assert event_with_registrations_and_priority.limit == limit
    assert registration.is_on_wait


@pytest.mark.django_db
def test_auto_bump_user_from_wait_does_not_increments_limit():
    """
    Tests if an automatic bump of a registration happens, the event limit wil not be incremented
    """
    event = EventFactory(limit=1)
    limit = event.limit
    priority = PriorityFactory(user_study=UserStudy.DATAING, user_class=UserClass.FIRST)
    event.registration_priorities.add(priority)

    user_not_in_priority_pool = UserFactory(
        user_study=UserStudy.DIGFOR.value, user_class=UserClass.SECOND.value
    )

    registration_to_delete = RegistrationFactory(event=event)
    registration_on_wait = RegistrationFactory(
        event=event, user=user_not_in_priority_pool
    )

    registration_to_delete.delete()

    registration_on_wait.refresh_from_db()
    event.refresh_from_db()
    assert not registration_on_wait.is_on_wait
    assert event.limit == limit
