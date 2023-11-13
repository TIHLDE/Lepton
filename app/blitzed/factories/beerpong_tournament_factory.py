import factory
from factory.django import DjangoModelFactory

from app.blitzed.models.beerpong_tournament import BeerpongTournament


class BeerpongTournamentFactory(DjangoModelFactory):
    class Meta:
        model = BeerpongTournament

    name = factory.Faker("sentence", nb_words=3)
