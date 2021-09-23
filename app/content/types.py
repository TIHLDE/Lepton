import graphene
from graphene_django import DjangoObjectType

from app.content.models import Event, Registration, User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"  # TODO: bad form


class RegistrationType(DjangoObjectType):
    class Meta:
        model = Registration
        fields = "__all__"


class EventType(DjangoObjectType):
    class Meta:
        model = Event
        fields = "__all__"  # TODO: bad form

    registrations = graphene.List(RegistrationType)

    def resolve_registrations(self, info, **kwargs):
        return self.registrations.all()
