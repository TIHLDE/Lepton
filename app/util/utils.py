import logging
from datetime import datetime, timedelta, timezone
from functools import wraps

from pytz import timezone as pytz_timezone

from app.common.enums import GroupType
from app.group.models import Group, Membership

logger = logging.getLogger(__name__)


def yesterday():
    return datetime.now(tz=timezone.utc) - timedelta(days=1)


def today():
    return datetime.now(tz=pytz_timezone("Europe/Oslo"))


def datetime_format(date_time):
    return date_time.strftime("%d %B, %Y")


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


def add_user_to_grade(user_id):
    grade = Group.objects.get_or_create(name=today().year, type=GroupType.STUDYYEAR)
    Membership.objects.get_or_create(user__user_id=user_id, group=grade)


def add_user_to_study(user_id, study):
    study = Group.objects.get_or_create(name=study)
    Membership.objects.get_or_create(user__user_id=user_id, group=study)
