#import factory
from factory.django import DjangoModelFactory

from app.wasted.models.session import Session


class SessionFactory(DjangoModelFactory):
    class Meta:
        model = Session
