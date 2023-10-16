import factory

from factory.django import DjangoModelFactory
from app.blitzed.models.beerpong_tournament import BeerpongTournament
from app.blitzed.factories.pong_match_factory import PongMatchFactory

class BeerpongTournamentFactory(DjangoModelFactory):
    class Meta:
        model = BeerpongTournament

    name = factory.Faker('sentence', nb_words=3)
    matches = factory.RelatedFactory(PongMatchFactory, 'tournaments') 
