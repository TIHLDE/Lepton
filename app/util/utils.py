from datetime import datetime, timezone, timedelta


def yesterday():
    return datetime.now(tz=timezone.utc)-timedelta(days=1)


def today():
    return datetime.now(tz=timezone.utc)
