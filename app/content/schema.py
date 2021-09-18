import graphene

from app.content.mutations import NewsMutation
from app.content.queries import NewsQuery, UserQuery


class Query(NewsQuery, UserQuery):
    pass


class Mutation(graphene.ObjectType):
    create_news = NewsMutation.Field()
