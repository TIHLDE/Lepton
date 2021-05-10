from django.template.loader import render_to_string

from celery import shared_task
from sentry_sdk import capture_exception

from app.content.models.notification import Notification
from app.content.models.registration import Registration
from app.content.models.strike import create_strike
from app.util.mailer import send_html_email


@shared_task
def event_sign_off_deadline_schedular():
    from app.content.models import Event
    # request_id = event_sign_off_deadline_schedular.request.id
    try:
      event = Event.objects.get(sign_off_deadline_schedular_id=event_sign_off_deadline_schedular.request.id)
      # if event.sign_off_deadline_schedular_id == request_id:
      print(event)
      for registration in Registration.objects.filter(event__pk=event.id, is_on_wait=False):
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
              user=registration.user, message="Påminnelse om avmeldingsfrist for " + event.title
          )
    except Event.DoesNotExist as event_not_exist:
        capture_exception(event_not_exist)


@shared_task
def event_end_schedular(pk, title, start_date, evaluate_link):
    for registration in Registration.objects.filter(event__pk=pk, has_attended=False):
        create_strike("NO_SHOW", registration.user, registration.event)
    for registration in Registration.objects.filter(event__pk=pk, has_attended=True):
        send_html_email(
            "Evaluering av " + title,
            render_to_string(
                "event_evaluation.html",
                context={
                    "user_name": registration.user.first_name,
                    "event_name": title,
                    "event_date": start_date,
                    "event_evaluate_link": evaluate_link,
                },
            ),
            registration.user.email,
        )


# TODO: Check if registration has answered the eval form.
@shared_task
def evaluation_form_answered_schedular():
    pass
