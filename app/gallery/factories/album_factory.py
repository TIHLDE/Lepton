import factory
from factory.django import DjangoModelFactory

from app.gallery.models.album import Album


class AlbumFactory(DjangoModelFactory):
    class Meta:
        model = Album

    id = factory.Sequence(lambda n: f"picture_{n}")
    image = factory.Faker("image")
    title = factory.Faker("title")
    image_alt = factory.Faker("image_alt")
    description = factory.Faker("description")
