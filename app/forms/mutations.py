import graphene
from graphene.types.scalars import Scalar

from app.forms.serializers import FormPolymorphicSerializer
from app.forms.types import FormUnionType
from app.graphql_core.generics import DRYGraphQLPermissions
from app.graphql_core.mutations import SerializerMutation


class ObjectField(Scalar):  # to serialize error message from serializer
    @staticmethod
    def serialize(dt):
        return dt


class Output:
    message = ObjectField()
    status = graphene.Int()


class FormMutation(SerializerMutation):
    permission_classes = [DRYGraphQLPermissions]
    serializer_class = FormPolymorphicSerializer
    model_operations = (
        "create",
        "update",
    )

    class Arguments:
        resource_type = graphene.String(required=True)
        title = graphene.String(required=True)

    form = graphene.Field(FormUnionType)

    @classmethod
    def resolve_mutation(cls, root, info, **kwargs):
        obj = super().resolve_mutation(root, info, **kwargs)
        return cls(form=obj)
