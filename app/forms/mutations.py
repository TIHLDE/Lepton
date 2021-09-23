from rest_framework import status
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


class Output:
    message = ObjectField()
    status = graphene.Int()


class DjangoMutation(graphene.Mutation, Output):
    serializer_class = None
    model_class = None

    @classmethod
    def resolve_mutation(cls, root, info, **kwargs):
        has_permission = cls.model_class.has_write_permission(request=info.context)

        if not has_permission:
            raise PermissionDenied

        serializer = cls.serializer_class(data=kwargs)
        if serializer.is_valid():
            obj = serializer.save()
            msg = "success"
            _status = status.HTTP_200_OK
        else:
            msg = serializer.errors
            obj = None
            _status = status.HTTP_400_BAD_REQUEST

        return cls(form=obj, message=msg, status=_status)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        return cls.resolve_mutation(root, info, **kwargs)


class FormMutation(DjangoMutation):
    serializer_class = FormPolymorphicSerializer
    model_class = Form

    class Arguments:
        resource_type = graphene.String(required=True)
        title = graphene.String(required=True)

    form = graphene.Field(FormUnionType)
