from datetime import timedelta

from django.utils import timezone


def get_payment_expiredate(event=None):
    if not event:
        return timezone.now() + timedelta(hours=12)

    return timezone.now() + timedelta(
        hours=event.paid_information.paytime.hour,
        minutes=event.paid_information.paytime.minute,
        seconds=event.paid_information.paytime.second,
    )
