import factory
from factory.django import DjangoModelFactory

from app.blitzed.factories.session_factory import SessionFactory
from app.blitzed.models.user_wasted_level import UserWastedLevel
from app.content.factories.user_factory import UserFactory


class UserWastedLevelFactory(DjangoModelFactory):
    class Meta:
        model = UserWastedLevel

    user = factory.SubFactory(UserFactory)
    session = factory.SubFactory(SessionFactory)
    blood_alcohol_level = factory.Faker("pydecimal", left_digits=1, right_digits=2)
    timestamp = factory.Faker("date_time_this_decade")
