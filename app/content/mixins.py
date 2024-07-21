from app.content.exceptions import (
    APIEventIsFullException,
    APIEventSignOffDeadlineHasPassed,
    APIHasStrikeException,
    APIUnansweredFormException,
    EventIsFullError,
    EventSignOffDeadlineHasPassed,
    StrikeError,
    UnansweredFormError,
    FeideTokenNotFoundError,
    FeideUserGroupsNotFoundError,
    FeideUserInfoNotFoundError,
    FeideUsernameNotFoundError,
    FeideGetTokenError,
    FeideGetUserInfoError,
    FeideGetUserGroupsError,
    FeideParseGroupsError,
    APIFeideTokenNotFoundException,
    APIFeideUserGroupsNotFoundException,
    APIFeideUserInfoNotFoundException,
    APIFeideUserNameNotFoundException,
    APIFeideGetTokenException,
    APIFeideGetUserInfoException,
    APIFeideGetUserGroupsException,
    APIFeideParseGroupsException
)
from app.util.mixins import APIErrorsMixin


class APIRegistrationErrorsMixin(APIErrorsMixin):
    @property
    def expected_exceptions(self):
        return {
            **super().expected_exceptions,
            EventSignOffDeadlineHasPassed: APIEventSignOffDeadlineHasPassed,
            UnansweredFormError: APIUnansweredFormException,
            StrikeError: APIHasStrikeException,
            EventIsFullError: APIEventIsFullException,
        }

class APIFeideUserErrorsMixin(APIErrorsMixin):
    @property
    def expected_exceptions(self):
        return {
            **super().expected_exceptions,
            FeideUsernameNotFoundError: APIFeideUserNameNotFoundException,
            FeideTokenNotFoundError: APIFeideTokenNotFoundException,
            FeideUserGroupsNotFoundError: APIFeideUserGroupsNotFoundException,
            FeideUserInfoNotFoundError: APIFeideUserInfoNotFoundException,
            FeideGetTokenError: APIFeideGetTokenException,
            FeideGetUserInfoError: APIFeideGetUserInfoException,
            FeideGetUserGroupsError: APIFeideGetUserGroupsException,
            FeideParseGroupsError: APIFeideParseGroupsException
        }