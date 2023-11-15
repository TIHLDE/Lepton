from rest_framework import status
from rest_framework.exceptions import APIException


class APIReactionNotAllowedException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Reaksjoner er ikke tillatt her"


class APIContentTypeNotSupportedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Er ikke støtte for denne typen"


class APIReactionDuplicateNotAllowedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Du har allerede reagert her"
