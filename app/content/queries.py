import graphene

from app.content.types import EventModelType


class EventQuery(graphene.ObjectType):
    retrieve_event, list_events = EventModelType.QueryFields()
