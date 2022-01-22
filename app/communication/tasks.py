from app.util.tasks import BaseTask
from app.celery import app

@app.task(bind=True, base=BaseTask)
def send_due_mails(self, *args, **kwargs):
    from django.db.models import Count
    from app.util.utils import now
    from app.communication.models.mail import Mail
    from app.communication.notifier import send_html_email

    mails_to_send = (Mail.objects.annotate(num_receivers=Count('users'))).filter(sent=False, eta__lt=now(), num_receivers__gt=0)
    mails_successfully_sent = 0

    for mail in mails_to_send:
        emails = (user.email for user in mail.users.all())
        is_success = send_html_email(to_mails=emails, html=mail.body, subject=mail.subject)
        if is_success:
            mail.sent = True
            mail.save(update_fields=['sent'])

            mails_successfully_sent += 1

    self.logger.info(f"Successfully sent: {mails_successfully_sent}/{mails_to_send.count()} mails")
