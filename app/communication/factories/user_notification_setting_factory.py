import factory
from factory.django import DjangoModelFactory

from app.communication.enums import UserNotificationSettingType
from app.communication.models import UserNotificationSetting
from app.content.factories.user_factory import UserFactory


class UserNotificationSettingFactory(DjangoModelFactory):
    class Meta:
        model = UserNotificationSetting

    user = factory.SubFactory(UserFactory)
    notification_type = UserNotificationSettingType.REGISTRATION
    email = True
    website = True
    slack = True
