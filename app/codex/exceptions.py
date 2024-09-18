from rest_framework import status
from rest_framework.exceptions import APIException


class APICodexCourseEndRegistrationDateAfterStartDate(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = (
        "Sluttdatoen for påmelding kan ikke være etter startdatoen for kurset"
    )


class APICodexCourseEndRegistrationDateBeforeStartRegistrationDate(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = (
        "Sluttdatoen for påmelding kan ikke være før startdatoen for påmelding"
    )


class CodexCourseEndRegistrationDateAfterStartDate(ValueError):
    pass


class CodexCourseEndRegistrationDateBeforeStartRegistrationDate(ValueError):
    pass
