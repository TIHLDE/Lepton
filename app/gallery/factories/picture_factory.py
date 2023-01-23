
import factory
from factory.django import DjangoModelFactory

from app.gallery.models.picture import Picture
from app.gallery.factories.albumFactory import AlbumFactory


class PictureFactory(DjangoModelFactory):
    class Meta:
        model = Picture

    id = factory.Sequence(lambda n: f'picture_{n}')
    image = factory.Faker('image')
    title = factory.Faker('title')
    image_alt = factory.Faker('image_alt')
    album = factory.SubFactory(AlbumFactory)
    description = factory.Faker('description')
    #write_access = AdminGroup.all()
