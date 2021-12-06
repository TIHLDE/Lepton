import logging
from datetime import datetime, timedelta
from functools import wraps

from django.conf import settings

from pytz import timezone as pytz_timezone

logger = logging.getLogger(__name__)


def getTimezone():
    return pytz_timezone(settings.TIME_ZONE)


def yesterday():
    return now() - timedelta(days=1)


def now():
    return datetime.now(tz=getTimezone())


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


def chunk_list(lst, n):
    """Chunk a list into smaller lists with a max-length of n"""
    lst = list(lst)
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def get_apposing_filter_kwargs(request, kwarg, not_kwarg, field_name):
    kwarg_param = request.query_params.get(kwarg, None)
    not_kwarg_param = request.query_params.get(not_kwarg, None)
    kwargs = {}
    if kwarg_param is not None:
        kwargs[field_name] = True

    if not_kwarg_param is not None and not kwarg_param:
        kwargs[field_name] = False

    if not_kwarg_param is not None and kwarg_param is not None:
        return {}
    return kwargs
