from rest_framework import status
from rest_framework.exceptions import APIException


class APIDuplicateSubmissionException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Spørreskjemaet tillater kun én innsending"


class DuplicateSubmission(ValueError):
    default_detail = "Spørreskjemaet tillater kun én innsending"


class APIFormNotOpenForSubmissionException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Spørreskjemaet er ikke åpent for innsending"


class FormNotOpenForSubmission(ValueError):
    default_detail = "Spørreskjemaet er ikke åpent for innsending"


class APIGroupFormOnlyForMembersException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Spørreskjemaet er kun åpent for medlemmer av gruppen"


class GroupFormOnlyForMembers(ValueError):
    default_detail = "Spørreskjemaet er kun åpent for medlemmer av gruppen"
