import graphene
from graphene.types.scalars import Scalar

from app.forms.models import Form
from app.forms.serializers import FormPolymorphicSerializer
from app.forms.types import FormUnionType
from app.graphql_core.generics import DRYGraphQLPermissions
from app.graphql_core.queries import ModelMutation


class ObjectField(Scalar):  # to serialize error message from serializer
    @staticmethod
    def serialize(dt):
        return dt


class Output:
    message = ObjectField()
    status = graphene.Int()


class FormMutation(ModelMutation):
    permission_classes = [DRYGraphQLPermissions]
    serializer_class = FormPolymorphicSerializer
    queryset = Form.objects.all()

    class Arguments:
        resource_type = graphene.String(required=True)
        title = graphene.String(required=True)

    form = graphene.Field(FormUnionType)
