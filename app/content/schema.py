import graphene

from app.content.mutations import EventMutation
from app.content.queries import EventQuery


class Query(EventQuery):
    pass


class Mutation(EventMutation, graphene.ObjectType):
    pass
