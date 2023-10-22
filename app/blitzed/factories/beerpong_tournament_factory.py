import factory
from factory.django import DjangoModelFactory

from app.blitzed.models.beerpong_tournament import BeerpongTournament


class BeerpongTournamentFactory(DjangoModelFactory):
    class Meta:
        model = BeerpongTournament

    name = factory.Faker("sentence", nb_words=3)

    @factory.post_generation
    def matches(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.matches.add(*extracted)

    @factory.post_generation
    def teams(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.teams.add(*extracted)
