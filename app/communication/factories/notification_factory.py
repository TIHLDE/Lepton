import factory
from factory.django import DjangoModelFactory

from app.communication.models.notification import Notification
from app.content.factories.user_factory import UserFactory


class NotificationFactory(DjangoModelFactory):
    class Meta:
        model = Notification

    user = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence")
    description = factory.Faker("paragraph")
    link = factory.Faker("safe_domain_name")
    read = False
