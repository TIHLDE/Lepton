from rest_framework import status
from rest_framework.exceptions import APIException


class APIDrawMatch(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Kan ikke kåre en vinner når stillingen er uavgjort"


class APIInvalidResult(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Ugyldig resultat"
