import factory

from factory.django import DjangoModelFactory
from app.blitzed.models.pong_team import PongTeam
from app.content.factories.user_factory import UserFactory
from app.blitzed.factories.anonymous_user_factory import AnonymousUserFactory

class NewsFactory(DjangoModelFactory):
    class Meta:
        model = PongTeam

    team_name = factory.Faker('sentence', nb_words=3)
    members = factory.SubFactory(UserFactory)
    anonymous_members = factory.SubFactory(AnonymousUserFactory)