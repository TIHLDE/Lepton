from rest_framework import status
from rest_framework.exceptions import APIException


class APICodexEventEndRegistrationDateAfterStartDate(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = (
        "Sluttdatoen for påmelding kan ikke være etter startdatoen for kurset"
    )


class APICodexEventEndRegistrationDateBeforeStartRegistrationDate(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = (
        "Sluttdatoen for påmelding kan ikke være før startdatoen for påmelding"
    )


class CodexEventEndRegistrationDateAfterStartDate(ValueError):
    pass


class CodexEventEndRegistrationDateBeforeStartRegistrationDate(ValueError):
    pass
