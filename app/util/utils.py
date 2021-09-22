import logging
from datetime import datetime, timedelta, timezone
from functools import wraps

from pytz import timezone as pytz_timezone

logger = logging.getLogger(__name__)


def yesterday():
    return datetime.now(tz=timezone.utc) - timedelta(days=1)


def today():
    return datetime.now(tz=pytz_timezone("Europe/Oslo"))


def datetime_format(date_time):
    from django.template import Context, Template

    # Using Django Template to format as it formats dates with both localization and timezone automatically
    return Template("{{ date_to_format }}").render(
        Context(dict(date_to_format=date_time))
    )


def midday(date_time):
    return date_time.replace(hour=12, minute=00, second=00)


def week_nr(date):
    return date.isocalendar()[1]


def disable_for_loaddata(signal_handler):
    """
    Disable signals for the 'loaddata' command
    to avoid conflicts while loading fixtures.
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get("raw", False):
            logger.info(f"Skipping signal for {args} {kwargs}")
            return
        signal_handler(*args, **kwargs)

    return wrapper


class CaseInsensitiveBooleanQueryParam:
    value = None

    def __init__(self, value):
        if value is not None:
            value = value.lower()
            if value == "true":
                self.value = True
            elif value == "false":
                self.value = False

    def __bool__(self):
        return bool(self.value)

    def __str__(self):
        return f"<{self.__class__.__name__} object ({self.value})"
