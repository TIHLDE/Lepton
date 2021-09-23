from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.generics import get_object_or_404

import graphene

from app.common.generics import DRYGraphQLPermissions
from app.forms.models import Form
from app.forms.types import FormUnionType


class RetrieveModelMixin:
    @classmethod
    def resolve_retrieve(cls, root, info, **kwargs):
        return cls.get_object(request=info.context, **kwargs)


class ListModelMixin:
    @classmethod
    def resolve_list(cls, root, info, **kwargs):
        cls.check_permissions(request=info.context)
        return cls.get_queryset()


# TODO: implement basic library checks
class GenericQuery:
    queryset = None
    permission_classes = []
    lookup_field = "pk"

    @classmethod
    def get_object(cls, request, **kwargs):

        # Perform the lookup filtering.
        lookup_url_kwarg = cls.lookup_field

        assert lookup_url_kwarg in kwargs, (
            "Expected query %s to be called with a variable "
            'named "%s". Fix your query definition or set the `.lookup_field` '
            "attribute on the query correctly."
            % (cls.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {cls.lookup_field: kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(cls.queryset, **filter_kwargs)

        # May raise a permission denied
        cls.check_object_permissions(request, obj)

        return obj

    @classmethod
    def get_queryset(cls):
        return cls.queryset

    @classmethod
    def permission_denied(cls, context, message=None, code=None):
        """
        If request is not permitted, determine what kind of exception to raise.
        """
        if context.user and not context.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail=message, code=code)

    @classmethod
    def check_permissions(cls, request):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in cls.get_permissions():
            if not permission.has_permission(request, cls):
                cls.permission_denied(
                    request,
                    message=getattr(permission, "message", None),
                    code=getattr(permission, "code", None),
                )

    @classmethod
    def check_object_permissions(cls, request, obj):
        """
        Check if the request should be permitted for a given object.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in cls.get_permissions():
            if not permission.has_object_permission(request, cls, obj):
                cls.permission_denied(
                    request,
                    message=getattr(permission, "message", None),
                    code=getattr(permission, "code", None),
                )

    @classmethod
    def get_permissions(cls):
        return cls.permission_classes


class ModelQuery(RetrieveModelMixin, ListModelMixin, GenericQuery):
    pass


class FormQuery(ModelQuery):
    queryset = Form.objects.all()
    permission_classes = [DRYGraphQLPermissions]
    lookup_field = "id"

    forms = graphene.List(FormUnionType)
    form = graphene.Field(FormUnionType, id=graphene.UUID())

    @classmethod
    def resolve_forms(cls, root, info, **kwargs):
        return super().resolve_list(root, info, **kwargs)

    @classmethod
    def resolve_form(cls, root, info, id, **kwargs):
        return super().resolve_retrieve(root, info, id=id)
