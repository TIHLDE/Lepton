from rest_framework import status
from rest_framework.exceptions import APIException


class APIDuplicateSubmissionException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Spørreskjemaet tillater kun én innsending"


class DuplicateSubmission(ValueError):
    pass


class APIFormNotOpenForSubmissionException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Spørreskjemaet er ikke åpent for innsending"


class FormNotOpenForSubmission(ValueError):
    pass


class APIGroupFormOnlyForMembersException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Spørreskjemaet er kun åpent for medlemmer av gruppen"


class GroupFormOnlyForMembers(ValueError):
    pass
