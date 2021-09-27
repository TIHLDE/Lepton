import graphene

from app.forms.serializers import FormPolymorphicSerializer
from app.forms.types import FormUnionType
from app.graphql.mutations import SerializerMutation
from app.graphql.permissions import DRYGraphQLPermissions


class FormMutation(SerializerMutation):
    class Meta:
        return_field_type = FormUnionType
        permission_classes = [DRYGraphQLPermissions]
        serializer_class = FormPolymorphicSerializer
        model_operations = (
            "create",
            "update",
        )

    class Arguments:
        resource_type = graphene.String(required=True)
        title = graphene.String(required=True)
        # fields = graphene.List(FieldType)
