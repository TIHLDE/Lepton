import factory

from factory.django import DjangoModelFactory
from app.blitzed.models.pong_match import PongMatch
from app.blitzed.factories.pong_team_factory import PongTeamFactory
from app.blitzed.factories.pong_result_factory import PongResultFactory

class PongMatchFactory(DjangoModelFactory):
    class Meta:
        model = PongMatch

    team1 = factory.SubFactory(PongTeamFactory)
    team2 = factory.SubFactory(PongTeamFactory)
    result = factory.SubFactory(PongResultFactory)
    prev_match = factory.LazyAttribute(lambda x: None)
