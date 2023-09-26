import factory

from factory.django import DjangoModelFactory

from app.content.models.comment import Comment
from app.content.factories.user_factory import UserFactory


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    body = factory.Faker("paragraph", nb_sentences=10)
    author = factory.SubFactory(UserFactory)
    parent = None
    