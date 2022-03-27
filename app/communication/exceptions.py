from rest_framework import status
from rest_framework.exceptions import APIException


class APIAllChannelsUnselected(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Du må velge minst en kommunikasjonsmetode"


class AllChannelsUnselected(ValueError):
    pass
