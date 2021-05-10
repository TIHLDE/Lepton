from django.template.loader import render_to_string

from celery import shared_task
from sentry_sdk import capture_exception

from app.content.models.notification import Notification
from app.content.models.registration import Registration
from app.content.models.strike import create_strike
from app.util.mailer import send_html_email
from app.util.utils import datetime_format


@shared_task
def event_sign_off_deadline_schedular():
    from app.content.models import Event

    try:
        event = Event.objects.get(
            sign_off_deadline_schedular_id=event_sign_off_deadline_schedular.request.id
        )
        for registration in Registration.objects.filter(
            event__pk=event.id, is_on_wait=False
        ):
            send_html_email(
                "Påminnelse om avmeldingsfrist for " + event.title,
                render_to_string(
                    "sign_off_deadline.html",
                    context={
                        "user_name": registration.user.first_name,
                        "event_name": event.title,
                        "event_id": event.id,
                    },
                ),
                registration.user.email,
            )
            Notification.objects.create(
                user=registration.user,
                message="Påminnelse om avmeldingsfrist for " + event.title,
            )
    except Event.DoesNotExist as event_not_exist:
        capture_exception(event_not_exist)


@shared_task
def event_end_schedular():
    from app.content.models import Event

    try:
        event = Event.objects.get(end_date_schedular_id=event_end_schedular.request.id)
        for registration in Registration.objects.filter(
            event__pk=event.id, has_attended=False
        ):
            create_strike("NO_SHOW", registration.user, registration.event)
        for registration in Registration.objects.filter(
            event__pk=event.id, has_attended=True
        ):
            send_html_email(
                "Evaluering av " + event.title,
                render_to_string(
                    "event_evaluation.html",
                    context={
                        "user_name": registration.user.first_name,
                        "event_name": event.title,
                        "event_date": datetime_format(event.start_date),
                        "event_evaluate_link": event.evaluate_link,
                    },
                ),
                registration.user.email,
            )
    except Event.DoesNotExist as event_not_exist:
        capture_exception(event_not_exist)


# TODO: Check if registration has answered the eval form.
@shared_task
def evaluation_form_answered_schedular():
    pass
