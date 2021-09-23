from rest_framework.exceptions import PermissionDenied

import graphene
from graphene.types.scalars import Scalar

from app.forms.models import Form
from app.forms.serializers import FormPolymorphicSerializer
from app.forms.types import FormUnionType


class ObjectField(Scalar):  # to serialize error message from serializer
    @staticmethod
    def serialize(dt):
        return dt


class DjangoMutation(graphene.Mutation):
    serializer = None
    model = None

    @classmethod
    def resolve_mutation(cls, root, info, **kwargs):
        has_permission = cls.model.has_write_permission(request=info.context)
        print(has_permission)

        if not has_permission:
            raise PermissionDenied


class FormMutation(DjangoMutation):
    form = graphene.Field(FormUnionType)
    message = ObjectField()
    status = graphene.Int()

    class Arguments:
        resource_type = graphene.String(required=True)
        title = graphene.String(required=True)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        has_permission = Form.has_write_permission(request=info.context)
        print(has_permission)
        if not has_permission:
            raise PermissionDenied

        serializer = FormPolymorphicSerializer(data=kwargs)
        if serializer.is_valid():
            obj = serializer.save()
            msg = "success"
        else:
            msg = serializer.errors
            obj = None
            print(msg)
        return cls(form=obj, message=msg, status=200)

    # form = graphene.Field()
