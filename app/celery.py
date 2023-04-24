from __future__ import absolute_import, unicode_literals

import os

from django.conf import settings

from celery import Celery
from celery.schedules import crontab

from app.util.tasks import BaseTask

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

app = Celery("app")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

schedule = {
    "send_due_mails": {
        "task": "app.communication.tasks.send_due_mails",
        # Every minute
        "schedule": crontab(),
    },
    "run_post_event_actions": {
        "task": "app.content.tasks.event.run_post_event_actions",
        # Every 15 minute between 12:00 and 13:00 every day to allow multiple attempts
        "schedule": crontab(minute="*/15", hour="12"),
    },
    "run_sign_off_deadline_reminder": {
        "task": "app.content.tasks.event.run_sign_off_deadline_reminder",
        # Every 15 minute between 12:00 and 13:00 every day to allow multiple attempts
        "schedule": crontab(minute="*/15", hour="12"),
    },
    "run_sign_up_start_notifier": {
        "task": "app.content.tasks.event.run_sign_up_start_notifier",
        # Every 5th minute
        "schedule": crontab(minute="*/5"),
    },
    "delete_log_entries": {
        "task": "app.common.tasks.delete_old_log_entries",
        # 12:00 every day
        "schedule": crontab(hour="12", minute="0"),
    },
}

app.conf.update(
    beat_schedule=schedule,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=settings.TIME_ZONE,
    enable_utc=True,
    task_always_eager=False
)

app.conf.task_always_eager = False


@app.task(bind=True, base=BaseTask)
def debug_task(self, *args, **kwargs):
    from app.util.utils import now

    self.logger.info(f"Debug, time: {now()}")
