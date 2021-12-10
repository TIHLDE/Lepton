from app.group.exceptions import APIUserIsNotInGroupException, UserIsNotInGroup
from app.util.mixins import APIErrorsMixin


class APIFineErrorsMixin(APIErrorsMixin):
    @property
    def expected_exceptions(self):
        return {
            **super().expected_exceptions,
            UserIsNotInGroup: APIUserIsNotInGroupException,
        }
