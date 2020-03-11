from celery import shared_task
from app.content.models.user_event import UserEvent
from app.util.mailer import send_html_email
from django.template.loader import render_to_string

@shared_task
def event_sign_off_deadline_schedular(pk, title):
  [send_html_email(
    "Påmindelse om avmeldingsfrist for " + title,
    render_to_string(
      'sign_off_deadline.html',
      context={'user_name':user_event.user.first_name, 'event_name':title, 'event_pk':pk}
    ),
    user_event.user.email
    ) for user_event in UserEvent.objects.filter(event__pk=pk, is_on_wait=False)]

@shared_task
def event_end_schedular(pk, title, date, evaluate_link):
  [send_html_email(
    "Evaluering av " + title,
    render_to_string(
      'event_evaluation.html',
      context={'user_name':user_event.user.first_name, 'event_name':title, 'event_date':date, 'event_evaluate_link':evaluate_link}
    ),
    user_event.user.email
    ) for user_event in UserEvent.objects.filter(event__pk=pk, has_attended=True)]

