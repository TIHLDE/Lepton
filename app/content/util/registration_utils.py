from datetime import datetime, timedelta


def get_payment_expiredate(event):
    return datetime.now() + timedelta(
        hours=event.paid_information.paytime.hour,
        minutes=event.paid_information.paytime.minute,
        seconds=event.paid_information.paytime.second,
    )
