from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError


class APIUserIsNotInGroupException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "En av brukerne er ikke medlem av gruppen"


class UserIsNotInGroup(ValidationError):
    pass


class APIGroupTypeNotInPublicGroupsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Ikke gylde gruppetype"


class GroupTypeNotInPublicGroups(ValueError):
    pass
