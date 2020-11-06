from django.template.loader import render_to_string

from celery import shared_task

from app.content.models.notification import Notification
from app.content.models.registration import Registration
from app.util.mailer import send_html_email


@shared_task
def event_sign_off_deadline_schedular(pk, title):
    for registration in Registration.objects.filter(event__pk=pk, is_on_wait=False):
        send_html_email(
            "Påmindelse om avmeldingsfrist for " + title,
            render_to_string(
                "sign_off_deadline.html",
                context={
                    "user_name": registration.user.first_name,
                    "event_name": title,
                    "event_pk": pk,
                },
            ),
            registration.user.email,
        )
        Notification.objects.create(
            user=registration.user, message="Påmindelse om avmeldingsfrist for " + title
        )


@shared_task
def event_end_schedular(pk, title, start_date, evaluate_link):
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
