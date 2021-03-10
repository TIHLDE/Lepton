import factory
from factory.django import DjangoModelFactory

from app.content.factories.user_factory import UserFactory
from app.content.models.notification import Notification


class NotificationFactory(DjangoModelFactory):
    class Meta:
        model = Notification

    user = factory.SubFactory(UserFactory)
    message = factory.Faker("sentence")
    read = False
