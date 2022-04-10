from app.communication.exceptions import (
    AllChannelsUnselected,
    AnotherVisibleBannerError,
    APIAllChannelsUnselected,
    APIAnotherVisibleBannerException,
    APIDatesMixedException,
    DatesMixedError,
)
from app.util.mixins import APIErrorsMixin


class APIBannerErrorsMixin(APIErrorsMixin):
    @property
    def expected_exceptions(self):
        return {
            **super().expected_exceptions,
            AnotherVisibleBannerError: APIAnotherVisibleBannerException,
            DatesMixedError: APIDatesMixedException,
        }


class APIUserNotificationSettingErrorsMixin(APIErrorsMixin):
    @property
    def expected_exceptions(self):
        return {
            **super().expected_exceptions,
            AllChannelsUnselected: APIAllChannelsUnselected,
        }
