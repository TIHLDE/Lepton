from celery import shared_task
from time import sleep
from ...util.mailer import send_tihlde_email


@shared_task
def reee():
  sleep(60)
  send_tihlde_email("Ree for mee", "Ree fortnite ty", ["zaim.imran@gmail.com"])
