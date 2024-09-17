from rest_framework import status
from rest_framework.exceptions import APIException


class APICodexCourseEndDateBeforeStartDate(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Sluttdatoen kan ikke være før startdatoen for kurset"


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


class APICodexCourseSignOffDeadlineAfterStartDate(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Avmeldingsfristen kan ikke være etter startdatoen for kurset"


class CodexCourseEndDateBeforeStartDate(ValueError):
    pass


class CodexCourseEndRegistrationDateAfterStartDate(ValueError):
    pass


class CodexCourseEndRegistrationDateBeforeStartRegistrationDate(ValueError):
    pass


class CodexCourseSignOffDeadlineAfterStartDate(ValueError):
    pass
