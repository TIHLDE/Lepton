from app.celery import app
from app.util.tasks import BaseTask
from django.db import transaction


@app.task(bind=True, base=BaseTask)
def send_due_mails(self, *args, **kwargs):
    from app.communication.models.mail import Mail
    from app.util.utils import now

    mails = Mail.objects.select_for_update().filter(eta__lt=now())
    total_mails = None
    mails_sent = 0
    with transaction.atomic():
        total_mails = mails.count()
        for mail in mails:
            is_success = mail.send()
            if is_success:
                mails_sent += 1

    self.logger.info(f"Successfully sent: {mails_sent}/{total_mails.count()} mails")
