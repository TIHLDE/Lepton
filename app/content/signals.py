import logging
from datetime import timedelta

from django.conf import settings

from sentry_sdk import capture_exception

from app.celery import app
from app.common.enums import EnvironmentOptions
from app.content.tasks.event import (
    event_end_schedular,
    event_sign_off_deadline_schedular,
)
from app.util.utils import disable_for_loaddata, midday, today

logger = logging.getLogger(__name__)


@disable_for_loaddata
def send_event_reminders(sender, instance, created, **kwargs):
    if (
        settings.ENVIRONMENT == EnvironmentOptions.PRODUCTION
        or settings.ENVIRONMENT == EnvironmentOptions.DEVELOPMENT
    ):
        run_celery_tasks_for_event(instance)


def run_celery_tasks_for_event(event):
    try:
        end_date_reminder(event)
        sign_off_deadline_reminder(event)
    except Exception as e:
        logging.info(e)
        capture_exception(e)


def end_date_reminder(event):
    eta = midday(event.end_date + timedelta(days=1))

    if (
        event.sign_up
        and not event.event_has_ended
        and not event.closed
        and isFuture(eta)
    ):
        try:
            app.control.revoke(event.end_date_schedular_id, terminate=True)
            new_task_id = event_end_schedular.apply_async(
                kwargs={"eventId": event.id, "eta": eta, "type": "end_date_reminder"},
                eta=(eta),
            )
            from app.content.models import Event

            Event.objects.filter(id=event.id).update(end_date_schedular_id=new_task_id)
        except Exception as e:
            capture_exception(e)


def sign_off_deadline_reminder(event):
    eta = midday(event.sign_off_deadline - timedelta(days=1))

    if (
        event.sign_up
        and not event.is_past_sign_off_deadline
        and not event.closed
        and isFuture(eta)
    ):
        try:
            app.control.revoke(event.sign_off_deadline_schedular_id, terminate=True)
            new_task_id = event_sign_off_deadline_schedular.apply_async(
                kwargs={
                    "eventId": event.id,
                    "eta": eta,
                    "type": "sign_off_deadline_reminder",
                },
                eta=(eta),
            )
            from app.content.models import Event

            Event.objects.filter(id=event.id).update(
                sign_off_deadline_schedular_id=new_task_id
            )
        except Exception as e:
            capture_exception(e)


def isFuture(eta):
    return eta > today()
