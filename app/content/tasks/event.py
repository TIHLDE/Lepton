from celery import shared_task
from time import sleep
from ...util.mailer import send_tihlde_email

from ...util.utils import today
import math

@shared_task
def event_unregister_deadline_mail(time):
  sleep(math.floor((time-today()).total_seconds()))
  send_tihlde_email("Tihlde sender test mail", "Tihlde sender test mail", ["zaim.imran@gmail.com"])

