from rest_framework import status
from rest_framework.exceptions import APIException


class APIPaidEventCantBeChangedToFreeEventException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Arrangementet er et betalt arrangement, og kan ikke endres til et gratis arrangement"


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
    default_detail = "Kan ikke melde deg på fordi du har en eller flere prikker"


class APIEventIsFullException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Du kan ikke flytte opp en fra ventelisten når arrangementet er fullt. Flytt en bruker ned først."


class EventSignOffDeadlineHasPassed(ValueError):
    pass


class StrikeError(ValueError):
    pass


class UnansweredFormError(ValueError):
    pass


class EventIsFullError(ValueError):
    pass
