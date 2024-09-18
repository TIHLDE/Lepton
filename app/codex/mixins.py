from app.codex.exceptions import (
    APICodexCourseEndRegistrationDateAfterStartDate,
    APICodexCourseEndRegistrationDateBeforeStartRegistrationDate,
    CodexCourseEndRegistrationDateAfterStartDate,
    CodexCourseEndRegistrationDateBeforeStartRegistrationDate,
)
from app.util.mixins import APIErrorsMixin


class APICodexCourseErrorsMixin(APIErrorsMixin):
    @property
    def expected_exceptions(self):
        return {
            **super().expected_exceptions,
            CodexCourseEndRegistrationDateAfterStartDate: APICodexCourseEndRegistrationDateAfterStartDate,
            CodexCourseEndRegistrationDateBeforeStartRegistrationDate: APICodexCourseEndRegistrationDateBeforeStartRegistrationDate,
        }
