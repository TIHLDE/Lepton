from app.communication.exceptions import (
    AllChannelsUnselected,
    APIAllChannelsUnselected,
)
from app.util.mixins import APIErrorsMixin


class APIUserNotificationSettingErrorsMixin(APIErrorsMixin):
    @property
    def expected_exceptions(self):
        return {
            **super().expected_exceptions,
            AllChannelsUnselected: APIAllChannelsUnselected,
        }
