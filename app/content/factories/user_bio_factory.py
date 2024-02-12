from django.contrib.contenttypes.models import ContentType

import factory
from factory.django import DjangoModelFactory

from app.content.factories.user_factory import UserFactory
from app.content.models.user_bio import UserBio

class UserBioFactory(DjangoModelFactory):
    class Meta:
        model = UserBio

    user = factory.SubFactory(UserFactory)


        