import logging
from datetime import timedelta

from celery.task.control import revoke

from app.content.tasks.event import (
    event_end_schedular,
    event_sign_off_deadline_schedular,
)
from app.util.utils import datetime_format, disable_for_loaddata, midday

logger = logging.getLogger(__name__)


@disable_for_loaddata
def send_event_reminders(sender, instance, created, **kwargs):
    run_celery_tasks_for_event(instance)


def run_celery_tasks_for_event(event):
    try:
        revoke(event.end_date_schedular_id, terminate=True)
        revoke(event.sign_off_deadline_schedular_id, terminate=True)
        if should_send_incoming_end_date_reminder(event):
            event.end_date_schedular_id = event_end_schedular.apply_async(
                eta=(midday(event.end_date + timedelta(days=1))),
                kwargs={
                    "pk": event.pk,
                    "title": event.title,
                    "start_date": datetime_format(event.start_date),
                    "evaluate_link": event.evaluate_link,
                },
            )
        if should_send_incoming_sign_off_deadline_reminder(event):
            event.sign_off_deadline_schedular_id = event_sign_off_deadline_schedular.apply_async(
                eta=(midday(event.sign_off_deadline - timedelta(days=1))),
                kwargs={"pk": event.pk, "title": event.title},
            )
        event.save()
    except Exception as e:
        logging.info(e)


def should_send_incoming_end_date_reminder(event):
    return event.evaluate_link and not event.event_has_ended and not event.closed


def should_send_incoming_sign_off_deadline_reminder(event):
    return event.sign_up and not event.is_past_sign_off_deadline and not event.closed
