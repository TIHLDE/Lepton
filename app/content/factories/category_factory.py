import factory

from factory.django import DjangoModelFactory

from app.content.models import Category


class CategoryFactory(DjangoModelFactory):
    """Factory that creates a generic category"""

    class Meta:
        model = Category

    text = factory.Faker("word")