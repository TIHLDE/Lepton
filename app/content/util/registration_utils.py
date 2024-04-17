from datetime import datetime, timedelta


def get_payment_expiredate():
    return datetime.now() + timedelta(hours=12)
