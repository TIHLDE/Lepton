import graphene

from app.graphql_core.generics import GenericSerializerMutation
from app.graphql_core.mixins import MutationMixin, SerializerMutationMixin


class SerializerMutation(
    MutationMixin, SerializerMutationMixin, GenericSerializerMutation, graphene.Mutation
):
    class Meta:
        abstract = True
