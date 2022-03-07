from datetime import timedelta
from unittest.mock import patch

import pytest

from app.content.factories import EventFactory
from app.content.tasks.event import (
    run_post_event_actions,
    run_sign_off_deadline_reminder,
    run_sign_up_start_notifier,
)
from app.util.utils import now


@pytest.mark.django_db
@patch("app.content.tasks.event.__sign_off_deadline_reminder")
def test_sign_off_deadline_reminder_is_called_when_not_runned_and_time_due(
    mock_sign_off_deadline_reminder,
):
    """Event sign off deadline reminder should be sent when not sent and the time is due"""
    EventFactory(sign_off_deadline=now() - timedelta(days=1))
    EventFactory(sign_off_deadline=now())
    EventFactory(sign_off_deadline=now() + timedelta(days=1))

    run_sign_off_deadline_reminder()

    assert mock_sign_off_deadline_reminder.call_count == 3


@pytest.mark.django_db
@patch("app.content.tasks.event.__sign_off_deadline_reminder")
def test_sign_off_deadline_reminder_is_not_called_when_time_not_due(
    mock_sign_off_deadline_reminder,
):
    """Event sign off deadline reminder should not be sent when the time is too far in the future"""
    EventFactory(sign_off_deadline=now() + timedelta(days=2))

    run_sign_off_deadline_reminder()

    assert not mock_sign_off_deadline_reminder.called


@pytest.mark.django_db
@patch("app.content.tasks.event.__sign_off_deadline_reminder")
def test_sign_off_deadline_reminder_is_not_called_when_already_runned(
    mock_sign_off_deadline_reminder,
):
    """Event sign off deadline reminder should not be sent when it has already runned"""
    EventFactory(sign_off_deadline=now(), runned_sign_off_deadline_reminder=True)

    run_sign_off_deadline_reminder()

    assert not mock_sign_off_deadline_reminder.called


@pytest.mark.django_db
@patch("app.content.tasks.event.__sign_off_deadline_reminder")
def test_sign_off_deadline_reminder_is_not_called_when_event_closed(
    mock_sign_off_deadline_reminder,
):
    """Event sign off deadline reminder should not be sent when the event is closed"""
    EventFactory(sign_off_deadline=now(), closed=True)

    run_sign_off_deadline_reminder()

    assert not mock_sign_off_deadline_reminder.called


@pytest.mark.django_db
@patch("app.content.tasks.event.__sign_off_deadline_reminder")
def test_sign_off_deadline_reminder_is_not_called_when_not_sign_up(
    mock_sign_off_deadline_reminder,
):
    """Event sign off deadline reminder should not be sent when the event.sign_up is false"""
    EventFactory(sign_off_deadline=now(), sign_up=False)

    run_sign_off_deadline_reminder()

    assert not mock_sign_off_deadline_reminder.called


@pytest.mark.django_db
def test_sign_off_deadline_reminder_set_runned_sign_off_deadline_reminder_to_true():
    """Event post event actions should set event.runned_sign_off_deadline_reminder to true"""
    event = EventFactory(sign_off_deadline=now())

    run_sign_off_deadline_reminder()

    event.refresh_from_db()

    assert event.runned_sign_off_deadline_reminder


@pytest.mark.django_db
@patch("app.content.tasks.event.__post_event_actions")
def test_post_event_actions_is_called_when_not_runned_and_time_due(
    mock_post_event_actions,
):
    """Event post event actions should be runned when not runned and the time is due"""
    EventFactory(end_date=now() - timedelta(days=2))
    EventFactory(end_date=now() - timedelta(days=1))

    run_post_event_actions()

    assert mock_post_event_actions.call_count == 2


@pytest.mark.django_db
@patch("app.content.tasks.event.__post_event_actions")
def test_post_event_actions_is_not_called_when_time_not_due(mock_post_event_actions):
    """Event post event actions should not be runned when the event ended today or has not ended yet"""
    EventFactory(end_date=now())
    EventFactory(end_date=now() + timedelta(days=1))

    run_post_event_actions()

    assert not mock_post_event_actions.called


@pytest.mark.django_db
@patch("app.content.tasks.event.__post_event_actions")
def test_post_event_actions_is_not_called_when_already_runned(mock_post_event_actions):
    """Event post event actions should not be runned when they have already runned"""
    EventFactory(end_date=now() - timedelta(days=1), runned_post_event_actions=True)

    run_post_event_actions()

    assert not mock_post_event_actions.called


@pytest.mark.django_db
@patch("app.content.tasks.event.__post_event_actions")
def test_post_event_actions_is_not_called_when_event_closed(mock_post_event_actions):
    """Event post event actions should not be runned when the event is closed"""
    EventFactory(end_date=now() - timedelta(days=1), closed=True)

    run_post_event_actions()

    assert not mock_post_event_actions.called


@pytest.mark.django_db
@patch("app.content.tasks.event.__post_event_actions")
def test_post_event_actions_is_not_called_when_not_sign_up(mock_post_event_actions):
    """Event post event actions should not be runned when event.sign_up is false"""
    EventFactory(end_date=now() - timedelta(days=1), sign_up=False)

    run_post_event_actions()

    assert not mock_post_event_actions.called


@pytest.mark.django_db
def test_post_event_actions_set_runned_post_event_actions_to_true():
    """Event post event actions should set event.runned_post_event_actions to true"""
    event = EventFactory(end_date=now() - timedelta(days=1))

    run_post_event_actions()

    event.refresh_from_db()

    assert event.runned_post_event_actions


@pytest.mark.django_db
@patch("app.content.tasks.event.__sign_up_start_notifier")
def test_sign_up_start_notifier_is_called_when_not_runned_and_time_due(
    mock_sign_up_start_notifier,
):
    """Event sign up start notifier should be runned when not runned and the time is due"""
    EventFactory()
    EventFactory(start_registration_at=now())

    run_sign_up_start_notifier()

    assert mock_sign_up_start_notifier.call_count == 2


@pytest.mark.django_db
@patch("app.content.tasks.event.__sign_up_start_notifier")
def test_sign_up_start_notifier_is_not_called_when_time_not_due(mock_sign_up_start_notifier):
    """Event sign up start notifier should not be runned when the event ended today or has not ended yet"""
    EventFactory(start_registration_at=now() + timedelta(minutes=1))

    run_sign_up_start_notifier()

    assert not mock_sign_up_start_notifier.called


@pytest.mark.django_db
@patch("app.content.tasks.event.__sign_up_start_notifier")
def test_sign_up_start_notifier_is_not_called_when_already_runned(mock_sign_up_start_notifier):
    """Event sign up start notifier should not be runned when they have already runned"""
    EventFactory(runned_sign_up_start_notifier=True)

    run_sign_up_start_notifier()

    assert not mock_sign_up_start_notifier.called


@pytest.mark.django_db
@patch("app.content.tasks.event.__sign_up_start_notifier")
def test_sign_up_start_notifier_is_not_called_when_event_closed(mock_sign_up_start_notifier):
    """Event sign up start notifier should not be runned when the event is closed"""
    EventFactory(closed=True)

    run_sign_up_start_notifier()

    assert not mock_sign_up_start_notifier.called


@pytest.mark.django_db
@patch("app.content.tasks.event.__sign_up_start_notifier")
def test_sign_up_start_notifier_is_not_called_when_not_sign_up(mock_sign_up_start_notifier):
    """Event sign up start notifier should not be runned when event.sign_up is false"""
    EventFactory(sign_up=False)

    run_sign_up_start_notifier()

    assert not mock_sign_up_start_notifier.called


@pytest.mark.django_db
def test_sign_up_start_notifier_set_runned_sign_up_start_notifier_to_true():
    """Event sign up start notifier should set event.runned_sign_up_start_notifier to true"""
    event = EventFactory()

    run_sign_up_start_notifier()

    event.refresh_from_db()

    assert event.runned_sign_up_start_notifier
