from django.utils import timezone

import factory
from factory.django import DjangoModelFactory

from app.communication.models.banner import Banner


class BannerFactory(DjangoModelFactory):
    class Meta:
        model = Banner

    title = factory.Sequence(lambda n: f"Banner {n}")
    description = factory.Faker("sentence", nb_words=5)
    visible_from = timezone.now()
    visible_until = timezone.now() + timezone.timedelta(days=1)
