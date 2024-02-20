from django.contrib.contenttypes.models import ContentType

import factory
from factory.django import DjangoModelFactory

from app.content.factories.news_factory import NewsFactory
from app.content.factories.user_factory import UserFactory
from app.content.models.comment import Comment
from app.content.models.news import News


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    author = factory.SubFactory(UserFactory)
    body = factory.Faker("paragraph", nb_sentences=10)
    content_object = factory.SubFactory(NewsFactory)

    @factory.lazy_attribute
    def content_type(self):
        return ContentType.objects.get_for_model(News)