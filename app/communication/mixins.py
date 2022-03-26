from app.communication.exceptions import (
    AnotherVisibleBannerError,
    APIAnotherVisibleBannerException,
    APIDatesMixedException,
    DatesMixedError,
    AllChannelsUnselected,
    APIAllChannelsUnselected,
)
from app.util.mixins import APIErrorsMixin


class APIBannerErrorsMixin(APIErrorsMixin):
    AnotherVisibleBannerError: APIAnotherVisibleBannerException,
    DatesMixedError: APIDatesMixedException,

      
class APIUserNotificationSettingErrorsMixin(APIErrorsMixin):
    @property
    def expected_exceptions(self):
        return {
            **super().expected_exceptions,
            AllChannelsUnselected: APIAllChannelsUnselected,
        }
