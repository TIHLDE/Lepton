import graphene

from app.content.types import EventType


class EventQuery(graphene.ObjectType):
    class Meta:
        pass

    list_events = graphene.List(EventType)
