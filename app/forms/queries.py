from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.generics import get_object_or_404

import graphene

from app.forms.models import Form
from app.forms.types import FormUnionType


class BaseQuery:
    queryset = None
    lookup_field = "pk"

    @classmethod
    def resolve_list(cls, root, info, **kwargs):
        cls.check_permissions(info)
        return cls.get_queryset()

    @classmethod
    def resolve_retrieve(cls, root, info, **kwargs):
        return cls.get_object(info, **kwargs)

    @classmethod
    def get_object(cls, info, **kwargs):

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
        cls.check_object_permissions(info, obj)

        return obj

    # TODO: Implement from dry_rest_permissions.generics.DRYPermissions and use it here
    @classmethod
    def check_permissions(cls, info):
        model_class = cls.queryset.model
        has_permission = model_class.has_list_permission(request=info.context)

        if not has_permission:
            cls.permission_denied(info)

    @classmethod
    def get_queryset(cls):
        return cls.queryset

    # TODO: Implement from dry_rest_permissions.generics.DRYPermissions and use it here
    @classmethod
    def check_object_permissions(cls, info, obj):
        has_retrieve_permission = obj.has_retrieve_permission(request=info.context)

        if not has_retrieve_permission:
            cls.permission_denied(info)

    @classmethod
    def permission_denied(cls, info, message=None, code=None):
        """
        If request is not permitted, determine what kind of exception to raise.
        """
        if info.context.user and not info.context.user.is_authenticated:
            raise NotAuthenticated()
        raise PermissionDenied(detail=message, code=code)


class FormQuery(BaseQuery):
    queryset = Form.objects.all()
    lookup_field = "id"

    forms = graphene.List(FormUnionType)
    form = graphene.Field(FormUnionType, id=graphene.UUID())

    @classmethod
    def resolve_forms(cls, root, info, **kwargs):
        return super().resolve_list(root, info, **kwargs)

    @classmethod
    def resolve_form(cls, root, info, id, **kwargs):
        return super().resolve_retrieve(root, info, id=id)
