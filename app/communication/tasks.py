from django.db import transaction

from app.celery import app
from app.util.tasks import BaseTask


@app.task(bind=True, base=BaseTask)
def send_due_mails(self, *_args, **_kwargs):
    from django.core.mail import get_connection

    from app.communication.models.mail import Mail
    from app.util.utils import now

    mails = Mail.objects.select_for_update().filter(eta__lt=now())
    total_mails = 0
    mails_sent = 0
    with transaction.atomic():
        # We don't have to make a connection here. If we don't a new connection is created per email.
        with get_connection() as connection:
            for mail in mails:
                is_success = mail.send(connection)
                if is_success:
                    mails_sent += 1
                total_mails += 1

    self.logger.info(f"Successfully sent: {mails_sent}/{total_mails} mails")
