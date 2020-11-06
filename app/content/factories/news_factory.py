import factory
from factory.django import DjangoModelFactory

from app.content.models.news import News


class NewsFactory(DjangoModelFactory):
    class Meta:
        model = News

    title = factory.Faker("sentence", nb_words=5)
    header = factory.Faker("sentence", nb_words=5)
    body = factory.Faker("paragraph", nb_sentences=10)
