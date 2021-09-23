import graphene

from app.forms.mutations import FormMutation
from app.forms.queries import FormQuery


class Query(FormQuery):
    pass


class Mutation(graphene.ObjectType):
    create_form = FormMutation.Field()
