import factory
from factory.django import DjangoModelFactory

from app.content.models.page import Page


class ParentPageFactory(DjangoModelFactory):
    class Meta:
        model = Page

    title = factory.Sequence(lambda n: f"Page{n}")
    slug = factory.Sequence(lambda n: f"Page{n}")
    parent = None
    content = factory.Faker("paragraph", nb_sentences=10)


class PageFactory(ParentPageFactory):
    class Meta:
        model = Page

    parent = factory.SubFactory(ParentPageFactory)
