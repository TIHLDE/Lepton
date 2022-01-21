from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from django.conf import settings

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
    'run-every-60-seconds': {
        'task': 'app.celery.debug_task',
        'schedule': 60.0
    },
}

app.conf.update(
    beat_schedule=schedule,
    task_serializer="json",
    accept_content=["json"],  # Ignore other content
    result_serializer="json",
    timezone=settings.TIME_ZONE,
    enable_utc=True
)


@app.task(bind=True, base=BaseTask)
def debug_task(self, *args, **kwargs):
    from app.util.utils import now

    self.logger.info(f"Test {now()}")
