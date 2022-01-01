from app.forms.exceptions import (
    APIDuplicateSubmissionException,
    APIFormNotOpenForSubmissionException,
    APIGroupFormOnlyForMembersException,
    DuplicateSubmission,
    FormNotOpenForSubmission,
    GroupFormOnlyForMembers,
)
from app.util.mixins import APIErrorsMixin


class APIFormErrorsMixin(APIErrorsMixin):
    @property
    def expected_exceptions(self):
        return {
            **super().expected_exceptions,
            DuplicateSubmission: APIDuplicateSubmissionException,
            FormNotOpenForSubmission: APIFormNotOpenForSubmissionException,
            GroupFormOnlyForMembers: APIGroupFormOnlyForMembersException,
        }
