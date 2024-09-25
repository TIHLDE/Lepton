from app.codex.exceptions import (
    APICodexEventEndRegistrationDateAfterStartDate,
    APICodexEventEndRegistrationDateBeforeStartRegistrationDate,
    CodexEventEndRegistrationDateAfterStartDate,
    CodexEventEndRegistrationDateBeforeStartRegistrationDate,
)
from app.util.mixins import APIErrorsMixin


class APICodexEventErrorsMixin(APIErrorsMixin):
    @property
    def expected_exceptions(self):
        return {
            **super().expected_exceptions,
            CodexEventEndRegistrationDateAfterStartDate: APICodexEventEndRegistrationDateAfterStartDate,
            CodexEventEndRegistrationDateBeforeStartRegistrationDate: APICodexEventEndRegistrationDateBeforeStartRegistrationDate,
        }
