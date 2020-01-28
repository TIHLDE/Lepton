from datetime import datetime, timezone, timedelta
from pytz import timezone as pytz_timezone


def yesterday():
    return datetime.now(tz=timezone.utc)-timedelta(days=1)


def today():
    return datetime.now(tz=pytz_timezone('Europe/Oslo'))
