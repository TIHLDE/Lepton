import factory

from factory.django import DjangoModelFactory

from django.contrib.contenttypes.models import ContentType

from app.content.models.comment import Comment
from app.content.models.event import Event
from app.content.models.news import News
from app.content.factories.user_factory import UserFactory
from app.content.factories.event_factory import EventFactory
from app.content.factories.news_factory import NewsFactory


class EventCommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    body = factory.Faker("paragraph", nb_sentences=10)
    author = factory.SubFactory(UserFactory)
    parent = None
    content_object = factory.SubFactory(EventFactory)

    @factory.lazy_attribute
    def content_type(self):
        return ContentType.objects.get_for_model(Event)


class NewsCommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    body = factory.Faker("paragraph", nb_sentences=10)
    author = factory.SubFactory(UserFactory)
    parent = None
    content_object = factory.SubFactory(NewsFactory)

    @factory.lazy_attribute
    def content_type(self):
        return ContentType.objects.get_for_model(News)
    