from app.content.exceptions import (
    APIEventSignOffDeadlineHasPassed,
    EventSignOffDeadlineHasPassed,
)
from app.util.mixins import APIErrorsMixin


class APIRegistrationErrorsMixin(APIErrorsMixin):
    @property
    def expected_exceptions(self):
        return {
            **super().expected_exceptions,
            EventSignOffDeadlineHasPassed: APIEventSignOffDeadlineHasPassed,
        }
