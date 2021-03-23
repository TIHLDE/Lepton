from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from kombu.utils.url import safequote

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

SAS_policy = "RootManageSharedAccessKey"  # SAS Policy
# Primary key from the previous SS
SAS_key = safequote("KbKoXjzKmX7hQ4UhVU5BNxe3+Z5xxpQnMqdhIgwNsQE=")
namespace = "dev-celery"

app = Celery("app", broker=f'azureservicebus://{SAS_policy}:{SAS_key}@{namespace}')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.update(
    task_serializer="json",
    accept_content=["json"],  # Ignore other content
    result_serializer="json",
    timezone="Europe/Oslo",
    enable_utc=True,
)


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
