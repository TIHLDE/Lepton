import factory

from factory.django import DjangoModelFactory
from app.blitzed.models.anonymous_user import AnonymousUser

class AnonymousUserFactory(DjangoModelFactory):
    class Meta:
        model = AnonymousUser

    name = factory.Faker("name")
