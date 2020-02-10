import os
from django.core.mail import send_mass_mail, send_mail


def send_tihlde_email(subject, message, mail_list):
  message = (subject, message, os.environ.get('EMAIL_USER'), mail_list)
  send_mail((message,), fail_silently=False)
  return None


def send_user_event_mail(is_on_wait, event, user):
  if is_on_wait:
    send_tihlde_email(
      "Du er satt på venteliste for event " + (event),
      "Inntil videre er du satt på venteliste",
      user
    )
  else:
    send_tihlde_email(
      "Du har fått plass på " + (event),
      "Gratulerer, du har fått plass på eventet " + (event),
      user
    )
  return None