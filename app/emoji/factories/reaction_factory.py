from django.contrib.contenttypes.models import ContentType

import factory
from factory.django import DjangoModelFactory

from app.content.factories.news_factory import NewsFactory
from app.content.factories.user_factory import UserFactory
from app.content.models.news import News
from app.emoji.models.reaction import Reaction


class NewsReactionFactory(DjangoModelFactory):
    class Meta:
        model = Reaction

    emoji = factory.Faker("emoji")
    user = factory.SubFactory(UserFactory)
    content_object = factory.SubFactory(NewsFactory)

    @factory.lazy_attribute
    def content_type(self):
        return ContentType.objects.get_for_model(News)
