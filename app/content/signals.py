from datetime import timedelta

from celery.task.control import revoke

from ..util.utils import today
from .tasks.event import event_end_schedular, event_sign_off_deadline_schedular


def send_event_reminders(sender, instance, created, **kwargs):
    if created:
        run_celery_tasks_for_event(instance)


def run_celery_tasks_for_event(event):
    revoke(event.end_date_schedular_id, terminate=True)
    revoke(event.sign_off_deadline_schedular_id, terminate=True)

    if should_send_incoming_end_date_reminder(event):
        event.end_date_schedular_id = event_end_schedular.apply_async(
            eta=(event.end_date + timedelta(days=1)),
            kwargs={
                "pk": event.pk,
                "title": event.title,
                "date": event.start_date,
                "evaluate_link": event.evaluate_link,
            },
        )
    if should_send_incoming_sign_off_deadline_reminder(event):
        event.sign_off_deadline_schedular_id = event_sign_off_deadline_schedular.apply_async(
            eta=(event.sign_off_deadline - timedelta(days=1)),
            kwargs={"pk": event.pk, "title": event.title},
        )


def should_send_incoming_end_date_reminder(event):
    return event.evaluate_link and event.end_date < today() and not event.closed


def should_send_incoming_sign_off_deadline_reminder(event):
    return event.sign_up and event.sign_off_deadline < today() and not event.closed
