import factory
from factory.django import DjangoModelFactory

from app.blitzed.factories.anonymous_user_factory import AnonymousUserFactory
from app.blitzed.models.pong_team import PongTeam
from app.content.factories.user_factory import UserFactory


class PongTeamFactory(DjangoModelFactory):
    class Meta:
        model = PongTeam

    team_name = factory.Faker("sentence", nb_words=3)
    # members = factory.List([
    #    factory.SubFactory(UserFactory) for _ in range(2)
    # ])
    # anonymous_members = factory.List([
    #    factory.SubFactory(AnonymousUserFactory) for _ in range(1)
    # ])
