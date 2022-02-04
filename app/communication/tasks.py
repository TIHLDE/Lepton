from app.celery import app
from app.util.tasks import BaseTask


@app.task(bind=True, base=BaseTask)
def send_due_mails(self, *args, **kwargs):
    from app.communication.models.mail import Mail
    from app.util.utils import now

    mails_to_send = Mail.objects.filter(sent=False, eta__lt=now())
    mails_successfully_sent = 0

    for mail in mails_to_send:
        is_success = mail.send()
        if is_success:
            mails_successfully_sent += 1

    self.logger.info(
        f"Successfully sent: {mails_successfully_sent}/{mails_to_send.count()} mails"
    )
