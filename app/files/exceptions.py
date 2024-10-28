from rest_framework import status
from rest_framework.exceptions import APIException


class FileDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Filen eksisterer ikke"


class FileDoesNotExist(ValueError):
    pass
