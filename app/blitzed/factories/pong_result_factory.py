import random

import factory
from factory.django import DjangoModelFactory

from app.blitzed.factories.pong_match_factory import PongMatchFactory
from app.blitzed.factories.pong_team_factory import PongTeamFactory
from app.blitzed.models.pong_result import PongResult


class PongResultFactory(DjangoModelFactory):
    class Meta:
        model = PongResult

    match = factory.SubFactory(PongMatchFactory)
    winner = factory.Faker(PongTeamFactory)
    result = factory.LazyAttribute(
        lambda _: f"{random.randint(0, 10)} - {random.randint(0, 10)}"
    )
