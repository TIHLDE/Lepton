import factory
from factory.django import DjangoModelFactory

from app.content.factories.user_factory import UserFactory
from app.content.models.short_link import ShortLink


class ShortLinkFactory(DjangoModelFactory):
    class Meta:
        model = ShortLink

    user = factory.SubFactory(UserFactory)
    name = factory.Faker("word")
    url = factory.Faker("uri")
