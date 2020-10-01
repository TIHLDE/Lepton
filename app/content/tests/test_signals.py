from unittest.mock import patch

import pytest

from ..factories import EventWithSignalsFactory


@pytest.mark.django_db
@patch("app.content.signals.run_celery_tasks_for_event")
def test_event_reminders_is_called_after_event_save(mock_run_celery_tasks_for_event):
    """Event reminders should be sent after event is successfully saved."""
    EventWithSignalsFactory()

    assert mock_run_celery_tasks_for_event.called_once
