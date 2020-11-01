from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.exceptions import APIException


class APIUserAlreadyAttendedEvent(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Brukeren har allerede ankommet")


class APIEventSignOffDeadlineHasPassed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Du kan ikke melde deg av etter avmeldingsfristen")


class EventSignOffDeadlineHasPassed(ValueError):
    pass
