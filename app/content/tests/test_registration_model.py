from unittest.mock import patch

from django.core.exceptions import ValidationError

import pytest

from app.common.enums import MembershipType
from app.content.factories import (
    EventFactory,
    PriorityPoolFactory,
    RegistrationFactory,
    StrikeFactory,
    UserFactory,
)
from app.forms.enums import EventFormType
from app.forms.models.forms import Submission
from app.forms.tests.form_factories import EventFormFactory, SubmissionFactory
from app.group.factories import GroupFactory, MembershipFactory

pytestmark = pytest.mark.django_db


def _add_user_to_group(user, group):
    return MembershipFactory(
        user=user, group=group, membership_type=MembershipType.MEMBER
    )


@pytest.fixture()
def user():
    return UserFactory()


@pytest.fixture()
def non_priority_group():
    return GroupFactory(name="Not prioritized group", slug="not_prioritized_group")


@pytest.fixture()
def priority_group():
    return GroupFactory(name="Prioritized group", slug="prioritized_group")


@pytest.fixture()
def user_in_priority_pool(priority_group):
    user = UserFactory()
    _add_user_to_group(user, priority_group)
    return user


@pytest.fixture()
def user_not_in_priority_pool(non_priority_group):
    user = UserFactory()
    _add_user_to_group(user, non_priority_group)
    return user


@pytest.fixture()
def event_with_priority_pool(priority_group):
    event = EventFactory(limit=1)
    PriorityPoolFactory(event=event, groups=(priority_group,))
    return event


@pytest.fixture()
def registration_not_in_priority_pool(
    event_with_priority_pool, user_not_in_priority_pool
):
    return RegistrationFactory(
        event=event_with_priority_pool, user=user_not_in_priority_pool
    )


@pytest.fixture()
def registration_in_priority_pool(event_with_priority_pool, user_in_priority_pool):
    return RegistrationFactory(
        event=event_with_priority_pool, user=user_in_priority_pool
    )


def test_swap_users_when_event_is_full(
    event_with_priority_pool, registration_not_in_priority_pool, user_in_priority_pool
):
    """Test that a prioritized user is swapped with a non prioritized user if the event is full."""

    registration_in_priority_pool = RegistrationFactory(
        event=event_with_priority_pool, user=user_in_priority_pool
    )

    registration_not_in_priority_pool.refresh_from_db()

    assert not registration_in_priority_pool.is_on_wait
    assert registration_not_in_priority_pool.is_on_wait


def test_bump_user_when_event_is_not_full(
    event_with_priority_pool,
    user_not_in_priority_pool,
    user_in_priority_pool,
):
    """
    Test that a non prioritized user is not swapped with
    a prioritized user if the event is not full.
    """
    event_with_priority_pool.limit = 10

    registration_not_in_priority_pool = RegistrationFactory(
        event=event_with_priority_pool, user=user_not_in_priority_pool
    )
    registration_in_priority_pool = RegistrationFactory(
        event=event_with_priority_pool, user=user_in_priority_pool
    )

    assert not registration_in_priority_pool.is_on_wait
    assert not registration_not_in_priority_pool.is_on_wait


def test_bump_user_when_user_is_not_in_priority_pool_and_event_is_full(
    event_with_priority_pool, user_not_in_priority_pool
):
    """Test that users are not swapped when new user is not prioritized and event is full."""
    registration_not_in_priority_pool = RegistrationFactory(
        event=event_with_priority_pool, user=user_not_in_priority_pool
    )
    other_user_not_in_priority_pool = UserFactory()
    other_registration_not_in_priority_pool = RegistrationFactory(
        event=event_with_priority_pool, user=other_user_not_in_priority_pool
    )

    assert not registration_not_in_priority_pool.is_on_wait
    assert other_registration_not_in_priority_pool.is_on_wait


def test_bump_user_without_event_priorities():
    """Test that users are not swapped when event does not have any priorities."""
    event = EventFactory(limit=1)

    registration_not_on_waiting_list = RegistrationFactory(
        event=event, user=UserFactory()
    )
    registration_on_waiting_list = RegistrationFactory(event=event, user=UserFactory())

    assert not registration_not_on_waiting_list.is_on_wait
    assert registration_on_waiting_list.is_on_wait


def test_that_bump_user_registers_on_waiting_list_when_no_one_to_swap_with_and_event_is_full(
    event_with_priority_pool,
    registration_in_priority_pool,
    priority_group,
):
    """
    Test that a prioritized user is put on waiting list
    if there is no one to swap places with and the event is full.
    """
    other_user_in_priority_pool = UserFactory()
    _add_user_to_group(other_user_in_priority_pool, priority_group)
    other_registration_in_priority_pool = RegistrationFactory(
        event=event_with_priority_pool, user=other_user_in_priority_pool
    )

    assert not registration_in_priority_pool.is_on_wait
    assert other_registration_in_priority_pool.is_on_wait


def test_swap_places_with_swaps_users(
    registration_in_priority_pool, registration_not_in_priority_pool
):
    """Should swap is_on_wait values for both users."""
    registration_in_priority_pool.swap_places_with(registration_not_in_priority_pool)

    assert not registration_in_priority_pool.is_on_wait
    assert registration_not_in_priority_pool.is_on_wait


def test_is_prioritized_when_user_in_priority_pool(registration_in_priority_pool):
    """Should return True when user is in a priority pool."""

    assert registration_in_priority_pool.is_prioritized


def test_is_prioritized_when_user_not_in_priority_pool(
    registration_not_in_priority_pool,
):
    """Should return False when user is not in a priority pool."""

    assert not registration_not_in_priority_pool.is_prioritized


def test_is_prioritized_when_user_in_group_priority_pool():
    """Should return True when user is in a group priority pool."""
    group = GroupFactory()
    event = EventFactory(limit=1)
    registration = RegistrationFactory(event=event)
    MembershipFactory(user=registration.user, group=group)
    PriorityPoolFactory(groups=[group], event=event)

    assert registration.is_prioritized


def test_is_prioritized_when_user_is_member_of_all_groups_in_priority_pool():
    """A prioritized user has to be a member of all groups of the priority pool."""
    group = GroupFactory()
    event = EventFactory(limit=1)
    registration = RegistrationFactory(event=event)
    MembershipFactory(user=registration.user, group=group)

    other_group = GroupFactory()
    MembershipFactory(user=registration.user, group=other_group)

    PriorityPoolFactory(groups=[group, other_group], event=event)
    PriorityPoolFactory(groups=[GroupFactory(), GroupFactory()], event=event)

    assert registration.is_prioritized


def test_is_prioritized_when_user_is_not_member_of_all_groups_in_priority_pool():
    """Should return false when user is not a member of all groups of the priority pool."""
    group = GroupFactory()
    event = EventFactory(limit=1)
    registration = RegistrationFactory(event=event)
    MembershipFactory(user=registration.user, group=group)

    other_group = GroupFactory()
    PriorityPoolFactory(groups=[group, other_group], event=event)

    assert not registration.is_prioritized


def test_is_prioritized_when_user_is_member_of_some_groups_across_all_priority_pools():
    """Should return false when user is only member of some of the groups across priority pools."""
    group = GroupFactory()
    event = EventFactory(limit=1)
    registration = RegistrationFactory(event=event)
    MembershipFactory(user=registration.user, group=group)

    other_group = GroupFactory()
    MembershipFactory(user=registration.user, group=other_group)

    PriorityPoolFactory(groups=[group, GroupFactory()], event=event)
    PriorityPoolFactory(groups=[other_group, GroupFactory()], event=event)

    assert not registration.is_prioritized


def test_is_prioritized_when_user_not_in_group_priority_pool():
    """Should return False when user is not in a group priority pool."""
    event = EventFactory(limit=1)
    PriorityPoolFactory(event=event, groups=[GroupFactory()])

    registration = RegistrationFactory(event=event)

    assert not registration.is_prioritized


@patch("app.content.models.registration.Registration.send_notification_and_mail")
def test_create_calls_send_notification_and_email(
    mock_send_notification_and_mail, event_with_priority_pool
):
    """send_notification_and_email should be called once during creation."""
    RegistrationFactory(event=event_with_priority_pool, user=UserFactory())

    assert mock_send_notification_and_mail.called_once


def test_create_when_event_has_waiting_list(
    event_with_priority_pool, registration_in_priority_pool
):
    """Should put user on waiting list if the event has a waiting list."""
    assert event_with_priority_pool.has_waiting_list()

    new_registration = RegistrationFactory(
        event=event_with_priority_pool, user=UserFactory()
    )

    assert new_registration.is_on_wait


def test_registration_in_queue_is_deleted_priority_in_waiting_list_is_moved_to_queue(
    event_with_priority_pool,
    registration_in_priority_pool,
    priority_group,
):
    """Swap registration when user is deleted with prioritized user."""
    user_in_priority_pool = UserFactory()
    _add_user_to_group(user_in_priority_pool, priority_group)
    other_registration_in_priority_pool = RegistrationFactory(
        event=event_with_priority_pool, user=user_in_priority_pool
    )
    user_not_in_priority_pool = UserFactory()
    registration_not_in_priority_pool = RegistrationFactory(
        event=event_with_priority_pool, user=user_not_in_priority_pool
    )

    registration_in_priority_pool.delete()
    other_registration_in_priority_pool.refresh_from_db()
    registration_not_in_priority_pool.refresh_from_db()

    assert not registration_in_priority_pool.event.registrations.filter(
        registration_id=registration_in_priority_pool.registration_id
    ).exists()
    assert not other_registration_in_priority_pool.is_on_wait
    assert registration_not_in_priority_pool.is_on_wait


def test_registration_in_queue_is_deleted_if_no_priority_registration_in_waiting_list_first_registration_is_moved_to_queue(
    event_with_priority_pool,
    registration_in_priority_pool,
):
    """Swap registration when user is deleted with first registration in waiting list, if no priority exists."""
    user_not_in_priority_pool = UserFactory()
    registration_not_in_priority_pool = RegistrationFactory(
        event=event_with_priority_pool, user=user_not_in_priority_pool
    )
    other_user_not_in_priority_pool = UserFactory()
    other_registration_not_in_priority_pool = RegistrationFactory(
        event=event_with_priority_pool,
        user=other_user_not_in_priority_pool,
    )

    registration_in_priority_pool.delete()
    registration_not_in_priority_pool.refresh_from_db()
    other_registration_not_in_priority_pool.refresh_from_db()

    assert not event_with_priority_pool.registrations.filter(
        registration_id=registration_in_priority_pool.registration_id
    ).exists()
    assert not registration_not_in_priority_pool.is_on_wait
    assert other_registration_not_in_priority_pool.is_on_wait


def test_registration_in_queue_is_deleted_if_no_waiting_list(
    event_with_priority_pool,
    registration_in_priority_pool,
):
    """Test that if there is no waiting list, a user is still able to unregister from an event"""
    registration_in_priority_pool.delete()
    event_with_priority_pool.refresh_from_db()

    assert not registration_in_priority_pool.event.registrations.filter(
        registration_id=registration_in_priority_pool.registration_id
    ).exists()
    assert not event_with_priority_pool.get_waiting_list().exists()


def test_delete_registration_when_no_users_on_wait_are_in_a_priority_pool_bumps_first_registration_on_wait(
    event_with_priority_pool,
):
    """
    Test that the first registration on wait is moved up when
    a registration is deleted and no registered users are prioritized.
    """
    user_not_in_priority_pool = UserFactory()

    registration_to_delete = RegistrationFactory(event=event_with_priority_pool)
    registration_on_wait = RegistrationFactory(
        event=event_with_priority_pool, user=user_not_in_priority_pool
    )

    registration_to_delete.delete()

    registration_on_wait.refresh_from_db()

    assert not registration_on_wait.is_on_wait


@pytest.mark.parametrize(
    "form_type,should_exist",
    [(EventFormType.EVALUATION, True), (EventFormType.SURVEY, False)],
)
def test_deleting_registration_deletes_submission(
    event_with_priority_pool, user, form_type, should_exist
):
    form = EventFormFactory(event=event_with_priority_pool, type=form_type)
    submission = SubmissionFactory(form=form, user=user)
    registration = RegistrationFactory(event=event_with_priority_pool, user=user)

    registration.delete()

    assert Submission.objects.filter(id=submission.id).exists() is should_exist


def test_create_registration_without_submission_answer_fails(
    event_with_priority_pool, user
):
    EventFormFactory(event=event_with_priority_pool, type=EventFormType.SURVEY)
    with pytest.raises(ValidationError):
        RegistrationFactory(event=event_with_priority_pool, user=user)


def test_bump_user_from_wait_when_event_is_full_does_not_increments_limit(
    event_with_priority_pool,
    registration_in_priority_pool,
):
    """
    Tests that event limit is not incremented
    when an admin attempts to bump a user up from the wait list when the event is full.
    """
    registration = RegistrationFactory(event=event_with_priority_pool)
    limit = event_with_priority_pool.limit
    registration.is_on_wait = False

    with pytest.raises(ValueError):
        registration.save()

    assert event_with_priority_pool.limit == limit


def test_attempted_bump_user_from_wait_when_event_is_full_does_not_bump_user(
    event_with_priority_pool,
    registration_in_priority_pool,
):
    """
    Tests that an admin cannot manualy bump a user up from the wait list when the event is full.
    """
    registration = RegistrationFactory(event=event_with_priority_pool)
    registration.is_on_wait = False

    with pytest.raises(ValueError):
        registration.save()

    registration.refresh_from_db()

    assert registration.is_on_wait


def test_bump_user_from_wait_does_not_increments_limit(
    event_with_priority_pool,
    registration_in_priority_pool,
):
    """
    Tests that an admin cannot manualy bump a user up from the wait list when the event is full.
    """
    registration = RegistrationFactory(event=event_with_priority_pool)
    limit = event_with_priority_pool.limit
    registration.is_on_wait = False

    with pytest.raises(ValueError):
        registration.save()

    registration.refresh_from_db()

    assert event_with_priority_pool.limit == limit
    assert registration.is_on_wait


def test_auto_bump_user_from_wait_does_not_increments_limit(event_with_priority_pool):
    """
    Tests if an automatic bump of a registration happens, the event limit wil not be incremented
    """
    limit = event_with_priority_pool.limit

    user_not_in_priority_pool = UserFactory()

    registration_to_delete = RegistrationFactory(event=event_with_priority_pool)
    registration_on_wait = RegistrationFactory(
        event=event_with_priority_pool, user=user_not_in_priority_pool
    )

    registration_to_delete.delete()

    registration_on_wait.refresh_from_db()
    event_with_priority_pool.refresh_from_db()
    assert not registration_on_wait.is_on_wait
    assert event_with_priority_pool.limit == limit


def test_set_attended_is_allowed_when_queue_exists():
    """
    Tests that admin can set participant as attended even if someone is on the waiting list
    """
    event = EventFactory(limit=1)
    registration = RegistrationFactory(event=event)
    RegistrationFactory(event=event, is_on_wait=True)
    new_attended_state = True
    registration.has_attended = new_attended_state

    registration.save()

    assert registration.has_attended == new_attended_state


def test_create_registration_on_priority_only_event_when_user_is_not_prioritized(
    event_with_priority_pool,
):
    """
    Tests if a user that is not prioritized throws an error when attempting to register
    on an event which is only open to prioritized users
    """
    event_with_priority_pool.only_allow_prioritized = True
    event_with_priority_pool.save()

    user_not_in_priority_pool = UserFactory()

    with pytest.raises(ValidationError):
        RegistrationFactory(
            event=event_with_priority_pool, user=user_not_in_priority_pool
        )


def test_create_registration_on_priority_only_event_when_user_is_prioritized(
    event_with_priority_pool, user_in_priority_pool
):
    """
    Tests if a user can register on an event that is only for prioritized users when the
    user is prioritized
    """
    event_with_priority_pool.only_allow_prioritized = True
    event_with_priority_pool.save()

    RegistrationFactory(event=event_with_priority_pool, user=user_in_priority_pool)


@pytest.mark.parametrize(
    ("enable_strikes"),
    [
        (False),
        (True),
    ],
)
def test_strikes_has_no_effect_if_event_has_strikes_disabled(
    event_with_priority_pool, user_in_priority_pool, enable_strikes
):
    """
    Tests if a user is prioritized even if they have 3 strikes, if the event
    has enforces_previous_strikes set to false
    """

    StrikeFactory(user=user_in_priority_pool, strike_size=3)
    event_with_priority_pool.only_allow_prioritized = True
    event_with_priority_pool.enforces_previous_strikes = enable_strikes
    event_with_priority_pool.save()

    registration = RegistrationFactory.build(
        event=event_with_priority_pool, user=user_in_priority_pool
    )
    is_prioritized = not enable_strikes
    assert registration.is_prioritized == is_prioritized


def test_wait_queue_number_is_null_when_not_in_wait_list(
    user_not_in_priority_pool, event_with_priority_pool
):
    registration_not_in_priority_pool = RegistrationFactory(
        event=event_with_priority_pool, user=user_not_in_priority_pool
    )

    assert registration_not_in_priority_pool.wait_queue_number is None


def test_wait_queue_number_is_correct_when_in_wait_list(
    user_not_in_priority_pool, event_with_priority_pool
):
    registration_not_in_priority_pool = RegistrationFactory(
        event=event_with_priority_pool, user=user_not_in_priority_pool
    )
    other_user_not_in_priority_pool = UserFactory()
    other_registration_not_in_priority_pool = RegistrationFactory(
        event=event_with_priority_pool, user=other_user_not_in_priority_pool
    )

    assert not registration_not_in_priority_pool.is_on_wait
    assert registration_not_in_priority_pool.wait_queue_number is None
    assert other_registration_not_in_priority_pool.is_on_wait == 1
