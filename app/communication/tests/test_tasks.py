from datetime import timedelta
from unittest.mock import patch

import pytest

from app.communication.factories import MailFactory
from app.communication.tasks import send_due_mails
from app.util.utils import now


@pytest.mark.django_db
@patch("app.communication.notifier.send_html_email")
def test_mail_is_sent_when_not_sent_and_due(mock_send_html_email):
    """Mail should be sent when not sent and the time is due"""
    MailFactory()

    send_due_mails()

    assert mock_send_html_email.called


@pytest.mark.django_db
@patch("app.communication.notifier.send_html_email")
def test_mail_is_not_sent_when_already_sent(mock_send_html_email):
    """Mail should be not sent when already sent"""
    MailFactory(sent=True)

    send_due_mails()

    assert not mock_send_html_email.called


@pytest.mark.django_db
@patch("app.communication.notifier.send_html_email")
def test_mail_is_not_sent_when_not_due(mock_send_html_email):
    """Mail should be not sent when not due"""
    MailFactory(eta=now() + timedelta(days=1))

    send_due_mails()

    assert not mock_send_html_email.called
