from celery import shared_task
from time import sleep
from ...util.mailer import send_tihlde_email

from django.core.mail import send_mass_mail, send_mail


@shared_task
def event_unregister_deadline_mail(time):
  sleep(int(time))
  print("-------------------------reeeeeeeeeeeeeee-------------------------")
  print(time)
  send_tihlde_email("Tihlde sender test mail", "Tihlde sender test mail", ["zaim.imran@gmail.com"])
  # send_mail("Tihlde sender test mail", "Tihlde sender test mail", os.environ.get('EMAIL_USER'), ["zaim.imran@gmail.com"], fail_silently=False,)

