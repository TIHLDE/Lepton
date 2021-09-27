from django.core.exceptions import ImproperlyConfigured
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.generics import get_object_or_404

import graphene
from graphene.types.mutation import MutationOptions
from graphene_django.types import ErrorType

from app.graphql_core.registry import registry
from app.graphql_core.utils import get_model_name


class GenericQuery:
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        description=None,
        permissions=None,
        _meta=None,
        error_type_class=None,
        error_type_field=None,
        errors_mapping=None,
        **options,
    ):
        if not _meta:
            _meta = ModelMutationOptions(cls)

        if isinstance(permissions, str):
            permissions = (permissions,)

        if permissions and not isinstance(permissions, tuple):
            raise ImproperlyConfigured(
                "Permissions should be a tuple or a string in Meta"
            )

        _meta.permissions = permissions
        _meta.error_type_class = error_type_class
        _meta.error_type_field = error_type_field
        _meta.errors_mapping = errors_mapping
        super().__init_subclass_with_meta__(
            description=description, _meta=_meta, **options
        )

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
                    request.context,
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
                    request.context,
                    message=getattr(permission, "message", None),
                    code=getattr(permission, "code", None),
                )

    @classmethod
    def get_permissions(cls):
        return cls.permission_classes

    @classmethod
    def get_model_class(cls):
        return cls.get_queryset().model


class ModelMutationOptions(MutationOptions):
    lookup_field = None
    model_class = None
    model_operations = ["create", "update"]
    serializer_class = None
    permission_classes = []
    exclude = None
    return_field_name = "instance"


class BaseMutation:
    errors = graphene.List(
        ErrorType, description="May contain more than one error for same field."
    )

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        description=None,
        permissions=None,
        _meta=None,
        error_type_class=None,
        error_type_field=None,
        errors_mapping=None,
        **options,
    ):
        if not _meta:
            _meta = ModelMutationOptions(cls)

        if isinstance(permissions, str):
            permissions = (permissions,)

        if permissions and not isinstance(permissions, tuple):
            raise ImproperlyConfigured(
                "Permissions should be a tuple or a string in Meta"
            )

        _meta.permissions = permissions
        _meta.error_type_class = error_type_class
        _meta.error_type_field = error_type_field
        _meta.errors_mapping = errors_mapping
        super().__init_subclass_with_meta__(
            description=description, _meta=_meta, **options
        )

    @classmethod
    def _update_mutation_arguments_and_fields(cls, arguments, fields):
        cls._meta.arguments.update(arguments)
        cls._meta.fields.update(fields)


class GenericSerializerMutation(BaseMutation, GenericQuery):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        arguments=None,
        model_class=None,
        serializer_class=None,
        exclude=None,
        return_field_name=None,
        _meta=None,
        **options,
    ):
        if not serializer_class:
            raise ImproperlyConfigured(
                "Field serializer_class is required for ModelMutation"
            )

        if not model_class:
            model_class = serializer_class.Meta.model

        if not _meta:
            _meta = ModelMutationOptions(cls)

        if exclude is None:
            exclude = []

        if not return_field_name:
            return_field_name = get_model_name(model_class)
        if arguments is None:
            arguments = {}

        _meta.model_class = model_class
        _meta.return_field_name = return_field_name
        _meta.serializer_class = serializer_class
        _meta.exclude = exclude
        super().__init_subclass_with_meta__(_meta=_meta, **options)

        model_type = cls.get_type_for_model()
        if not model_type:
            raise ImproperlyConfigured(
                "Unable to find type for model %s in graphene registry"
                % model_class.__name__
            )
        fields = {return_field_name: graphene.Field(model_type)}

        cls._update_mutation_arguments_and_fields(arguments=arguments, fields=fields)

    @classmethod
    def get_type_for_model(cls):
        return registry.get_type_for_model(cls._meta.model_class)

    @classmethod
    def get_serializer(cls, root, info, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = cls.get_serializer_class()
        serializer_kwargs = cls.get_serializer_kwargs(root, info, **kwargs)
        return serializer_class(*args, **serializer_kwargs)

    @classmethod
    def get_serializer_class(cls):
        """
        Return the class to use for the serializer.
        Defaults to using `cls.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        assert cls._meta.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method." % cls.__class__.__name__
        )

        return cls._meta.serializer_class

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        lookup_field = cls.get_lookup_field()
        model_class = cls.get_model_class()
        model_operations = cls.get_model_operations()

        if model_class:
            if "update" in model_operations and lookup_field in input:
                instance = get_object_or_404(
                    model_class, **{lookup_field: input[lookup_field]}
                )
                partial = True
            elif "create" in model_operations:
                instance = None
                partial = False
            else:
                raise Exception(
                    'Invalid update operation. Input parameter "{}" required.'.format(
                        lookup_field
                    )
                )

            return {
                "instance": instance,
                "data": input,
                "context": {"request": info.context},
                "partial": partial,
            }

        return {"data": input, "context": {"request": info.context}}

    @classmethod
    def get_lookup_field(cls):
        model_class = cls.get_model_class()

        if not cls.lookup_field and model_class:
            return model_class._meta.pk.name

        return cls._meta.lookup_field

    @classmethod
    def get_model_class(cls):
        return cls.get_serializer_class().Meta.model

    @classmethod
    def get_model_operations(cls):

        assert (
            "update" in cls._meta.model_operations
            and "create" in cls._meta.model_operations
        ), "model_operations must contain 'create' and/or 'update'"

        return cls._meta.model_operations
