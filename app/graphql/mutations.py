import graphene

from app.graphql.generics import GenericSerializerMutation
from app.graphql.mixins import MutationMixin, SerializerMutationMixin


class SerializerMutation(
    MutationMixin, SerializerMutationMixin, GenericSerializerMutation, graphene.Mutation
):
    class Meta:
        abstract = True
