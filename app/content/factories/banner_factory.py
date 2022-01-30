import factory
from factory.django import DjangoModelFactory

from app.content.models.banner import Banner
from app.util.utils import now


class BannerFactory(DjangoModelFactory):
    class Meta:
        model = Banner

    title = factory.Faker("sentence", nb_words=5)
    description = factory.Faker("sentence", nb_words=5)
    visible_from = now()
