from datetime import timedelta
from app.util.tasks import BaseTask
from app.celery import app

from sentry_sdk import capture_exception

from app.celery import app
from app.util.utils import now, midnight


@app.task(bind=True, base=BaseTask)
def run_post_event_actions(self, *args, **kwargs):
    from app.content.models.event import Event
    from app.content.tasks.event import post_event_actions

    try:
        events = Event.objects.filter(runned_post_event_actions=False, sign_up=True, closed=False, end_date__lt=midnight(now()))

        for event in events:
            post_event_actions(event)
    except Exception as e:
            capture_exception(e)

@app.task(bind=True, base=BaseTask)
def run_sign_off_deadline_reminder(self, *args, **kwargs):
    from app.content.models.event import Event
    from app.content.tasks.event import sign_off_deadline_reminder

    try:
        events = Event.objects.filter(runned_post_event_actions=False, sign_up=True, closed=False, sign_off_deadline__lt=midnight(now() + timedelta(days=2)))

        for event in events:
            sign_off_deadline_reminder(event)
    except Exception as e:
            capture_exception(e)
