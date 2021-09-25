import graphene

from app.content.types import EventModelType


class EventMutation(graphene.ObjectType):
    create_event, delete_event, update_event = EventModelType.MutationFields()
