from app.group.exceptions import APIUserIsNotInGroupException, APIGroupTypeNotInPublicGroupsException, UserIsNotInGroup, GroupTypeNotInPublicGroups
from app.util.mixins import APIErrorsMixin


class APIFineErrorsMixin(APIErrorsMixin):
    @property
    def expected_exceptions(self):
        return {
            **super().expected_exceptions,
            UserIsNotInGroup: APIUserIsNotInGroupException,
        }


class APIGroupErrorsMixin(APIErrorsMixin):
    @property
    def expected_exceptions(self):
        return {
            **super().expected_exceptions,
            GroupTypeNotInPublicGroups: APIGroupTypeNotInPublicGroupsException
        }
