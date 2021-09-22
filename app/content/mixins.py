from app.content.exceptions import (
    APIEventSignOffDeadlineHasPassed,
    APIHasStrikeException,
    APIUnansweredFormException,
    EventSignOffDeadlineHasPassed,
    StrikeError,
    UnansweredFormError,
)
from app.util.mixins import APIErrorsMixin


class APIRegistrationErrorsMixin(APIErrorsMixin):
    @property
    def expected_exceptions(self):
        return {
            **super().expected_exceptions,
            EventSignOffDeadlineHasPassed: APIEventSignOffDeadlineHasPassed,
            UnansweredFormError: APIUnansweredFormException, 
            StrikeError : APIHasStrikeException,
        }
