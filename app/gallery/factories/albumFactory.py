import factory
from factory.django import DjangoModelFactory

from app.gallery.models.picture import Picture
#from app.content.factories.event_factory import EventFactory


class AlbumFactory(DjangoModelFactory):
    class Meta:
        model = Picture

    id = factory.Sequence(lambda n: f'album_{n}')
    title = factory.Faker('title')
    #event = factory.SubFactory(EventFactory)
    description = factory.Faker('description')
    #slug = factory.SlugField(f'{self.title}') #models.SlugField(max_length=50, primary_key=False)
    #write_access = AdminGroup.all()
