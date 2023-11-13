import factory
from factory.django import DjangoModelFactory

from app.blitzed.models.session import Session
from app.content.factories.user_factory import UserFactory


class SessionFactory(DjangoModelFactory):
    class Meta:
        model = Session

    creator = factory.SubFactory(UserFactory)
    start_time = factory.Faker("date_time_this_decade")
    end_time = factory.Faker("date_time_this_decade", before_now=True)
