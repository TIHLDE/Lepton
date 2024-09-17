from app.codex.exceptions import (
    APICodexCourseEndDateBeforeStartDate,
    APICodexCourseEndRegistrationDateAfterStartDate,
    APICodexCourseEndRegistrationDateBeforeStartRegistrationDate,
    APICodexCourseSignOffDeadlineAfterStartDate,
    CodexCourseEndDateBeforeStartDate,
    CodexCourseEndRegistrationDateAfterStartDate,
    CodexCourseEndRegistrationDateBeforeStartRegistrationDate,
    CodexCourseSignOffDeadlineAfterStartDate,
)
from app.util.mixins import APIErrorsMixin


class APICodexCourseErrorsMixin(APIErrorsMixin):
    @property
    def expected_exceptions(self):
        return {
            **super().expected_exceptions,
            CodexCourseEndDateBeforeStartDate: APICodexCourseEndDateBeforeStartDate,
            CodexCourseEndRegistrationDateAfterStartDate: APICodexCourseEndRegistrationDateAfterStartDate,
            CodexCourseEndRegistrationDateBeforeStartRegistrationDate: APICodexCourseEndRegistrationDateBeforeStartRegistrationDate,
            CodexCourseSignOffDeadlineAfterStartDate: APICodexCourseSignOffDeadlineAfterStartDate,
        }
