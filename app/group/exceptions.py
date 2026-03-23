from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError


class APIUserIsNotInGroupException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "En av brukerne er ikke medlem av gruppen"


class UserIsNotInGroup(ValidationError):
    default_detail = "En av brukerne er ikke medlem av gruppen"


class APIGroupTypeNotInPublicGroupsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Ikke gylde gruppetype"


class GroupTypeNotInPublicGroups(ValueError):
    default_detail = "Ikke gylde gruppetype"


class APISubtypeNotAllowedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Undertype er kun tillatt for interessegrupper"


class SubtypeNotAllowed(ValueError):
    default_detail = "Undertype er kun tillatt for interessegrupper"
