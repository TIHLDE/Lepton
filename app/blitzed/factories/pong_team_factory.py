import factory
from factory.django import DjangoModelFactory

from app.blitzed.factories.beerpong_tournament_factory import (
    BeerpongTournamentFactory,
)
from app.blitzed.models.pong_team import PongTeam


class PongTeamFactory(DjangoModelFactory):
    class Meta:
        model = PongTeam

    team_name = factory.Faker("sentence", nb_words=3)
    tournament = factory.SubFactory(BeerpongTournamentFactory)
    icon_id = "shark"

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.members.add(*extracted)

    @factory.post_generation
    def anonymous_members(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.anonymous_members.add(*extracted)
