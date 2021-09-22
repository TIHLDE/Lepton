from rest_framework import status
from rest_framework.exceptions import APIException


class APIUserAlreadyAttendedEvent(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Brukeren har allerede ankommet"


class APIEventSignOffDeadlineHasPassed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Du kan ikke melde deg av etter avmeldingsfristen"


class APIUnansweredFormException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = (
        "Du har ubesvarte evalueringsskjemaer som må besvares før du kan melde deg på"
    )


class APIHasStrikeException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Kan ikke melde deg på fordi du har en prikk"


class EventSignOffDeadlineHasPassed(ValueError):
    pass


class StrikeError(ValueError):
    pass


class UnansweredFormError(ValueError):
    pass
