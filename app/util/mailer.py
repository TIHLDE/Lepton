import os

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from sentry_sdk import capture_exception

from app.content.models.notification import Notification


def send_html_email(subject, html, mail_list):
    try:
        text_content = strip_tags(html)
        msg = EmailMultiAlternatives(
            subject, text_content, os.environ.get("EMAIL_USER"), [mail_list]
        )
        msg.attach_alternative(html, "text/html")
        msg.send()
    except Exception as send_html_email_fail:
        capture_exception(send_html_email_fail)


def send_event_waitlist(registration):
    send_html_email(
        "Venteliste for " + registration.event.title,
        render_to_string(
            "waitlist.html",
            context={
                "user_name": registration.user.first_name,
                "event_name": registration.event.title,
                "event_deadline": registration.event.sign_off_deadline,
            },
        ),
        registration.user.email,
    )
    Notification(
        user=registration.user,
        message="På grunn av høy pågang er du satt på venteliste på "
        + registration.event.title,
    ).save()


def send_event_verification(registration):
    send_html_email(
        "Plassbekreftelse for " + registration.event.title,
        render_to_string(
            "signed_up.html",
            context={
                "user_name": registration.user.first_name,
                "event_name": registration.event.title,
                "event_time": registration.event.start_date,
                "event_place": registration.event.location,
                "event_deadline": registration.event.sign_off_deadline,
            },
        ),
        registration.user.email,
    )
    Notification(
        user=registration.user,
        message="Du har fått plass på " + registration.event.title,
    ).save()
