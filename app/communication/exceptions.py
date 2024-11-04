from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.exceptions import APIException


class APIAnotherVisibleBannerException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Det finnes allerede et banner som er synlig i samme tidsrom"


class AnotherVisibleBannerError(ValidationError):
    default_detail = "Det finnes allerede et banner som er synlig i samme tidsrom"


class APIDatesMixedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Datoen banneret er synlig til er satt etter datoen banneret for synlig fra. Bytt om disse to"


class DatesMixedError(ValidationError):
    default_detail = "Datoen banneret er synlig til er satt etter datoen banneret for synlig fra. Bytt om disse to"


class APIAllChannelsUnselected(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Du må velge minst en kommunikasjonsmetode"


class AllChannelsUnselected(ValueError):
    default_detail = "Du må velge minst en kommunikasjonsmetode"
