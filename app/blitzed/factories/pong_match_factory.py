import factory
from factory.django import DjangoModelFactory

from app.blitzed.factories.beerpong_tournament_factory import (
    BeerpongTournamentFactory,
)
from app.blitzed.factories.pong_team_factory import PongTeamFactory
from app.blitzed.models.pong_match import PongMatch


class PongMatchFactory(DjangoModelFactory):
    class Meta:
        model = PongMatch

    team1 = factory.SubFactory(PongTeamFactory)
    team2 = factory.SubFactory(PongTeamFactory)
    future_match = factory.LazyAttribute(lambda x: None)
    tournament = factory.SubFactory(BeerpongTournamentFactory)