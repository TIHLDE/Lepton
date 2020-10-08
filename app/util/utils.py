import logging
from datetime import datetime, timedelta, timezone
from functools import wraps

from pytz import timezone as pytz_timezone

logger = logging.getLogger(__name__)


def yesterday():
    return datetime.now(tz=timezone.utc) - timedelta(days=1)


def today():
    return datetime.now(tz=pytz_timezone("Europe/Oslo"))


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
