# import factory
from factory.django import DjangoModelFactory

from app.blitzed.models.session import Session


class SessionFactory(DjangoModelFactory):
    class Meta:
        model = Session
