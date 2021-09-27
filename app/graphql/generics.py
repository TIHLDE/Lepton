from abc import abstractmethod

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db.models import QuerySet
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.generics import get_object_or_404

import graphene
from graphene_django.types import ErrorType

from app.graphql.options import ModelMutationOptions, ModelOptions
from app.graphql.registry import registry
from app.graphql.utils import get_model_name


class GenericObjectType(graphene.ObjectType):
    class Meta:
        abstract = True

    @classmethod
    def get_object(cls, request, **kwargs):
        # Perform the lookup filtering.
        lookup_url_kwarg = cls.get_lookup_field()

        assert lookup_url_kwarg in kwargs, (
            "Expected query %s to be called with a variable "
            'named "%s". Fix your query definition or set the `.lookup_field` '
            "attribute on the query correctly."
            % (cls.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {lookup_url_kwarg: kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(cls.get_model_class(), **filter_kwargs)

        # May raise a permission denied
        cls.check_object_permissions(request, obj)

        return obj

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
    @abstractmethod
    def get_permissions(cls):
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_lookup_field(cls):
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_queryset(cls):
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_model_class(cls):
        raise NotImplementedError()


class GenericQuery(GenericObjectType, ModelOptions):
    @classmethod
    def get_model_class(cls):
        return cls.get_queryset().model

    @classmethod
    def get_queryset(cls):
        if cls.queryset and not isinstance(cls.queryset, QuerySet):
            raise ImproperlyConfigured(
                "queryset should be a defined and be an instance of QuerySet in class Meta"
            )
        return cls.queryset

    @classmethod
    def get_permissions(cls):
        return cls.permissions

    @classmethod
    def get_lookup_field(cls):
        lookup_url_kwarg = cls.lookup_field
        return lookup_url_kwarg


class BaseMutation(GenericObjectType):

    errors = graphene.List(
        ErrorType, description="May contain more than one error for same field."
    )

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        arguments=None,
        description=None,
        _meta=None,
        lookup_field="pk",
        model_operations=("create", "update"),
        permissions=(),
        model=None,
        exclude=None,
        return_field_name=None,
        return_field_type=None,
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

        if not model:
            raise ImproperlyConfigured("model must be defined for Mutation")

        model_type = (
            return_field_type if return_field_type else cls.get_type_for_model()
        )

        if exclude is None:
            exclude = []
        if not return_field_name:
            return_field_name = get_model_name(model)
        if arguments is None:
            arguments = {}

        _meta.permissions = permissions
        _meta.lookup_field = lookup_field
        _meta.description = description
        _meta.model_operations = model_operations
        _meta.return_field_name = return_field_name
        _meta.return_field_type = return_field_type
        _meta.model = model
        _meta.exclude = exclude

        super().__init_subclass_with_meta__(
            description=description, _meta=_meta, **options
        )

        if not model_type and not return_field_type:
            raise ImproperlyConfigured(
                f"return_field_type was not specified in Meta and type for model {model.__name__} "
                "was not found in graphene registry."
            )
        fields = {return_field_name: graphene.Field(model_type)}

        cls._update_mutation_arguments_and_fields(arguments=arguments, fields=fields)

    @classmethod
    def _update_mutation_arguments_and_fields(cls, arguments, fields):
        cls._meta.arguments.update(arguments)
        cls._meta.fields.update(fields)

    @classmethod
    def resolve_mutation(cls, root, info, **data):
        cls.check_permissions(info)
        return cls.mutate_and_get_payload(root, info, **data)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        try:
            response = cls.perform_mutate(root, info, **data)
            if response.errors is None:
                response.errors = []
            return cls.success_response(response)
        except ValidationError as e:
            return cls.handle_errors(e)

    @classmethod
    def perform_mutate(cls, serializer, info):
        pass

    @classmethod
    def handle_errors(cls, error, **extra):  # TODO
        # error_list = validation_error_to_error_type(error, cls._meta.error_type_class)
        return cls.handle_typed_errors([error], **extra)

    @classmethod
    def handle_typed_errors(cls, errors, **extra):
        """Return class instance with errors."""
        if cls._meta.error_type_field is not None:
            extra.update({cls._meta.error_type_field: errors})
        return cls(errors=errors, **extra)

    @classmethod
    def get_permissions(cls):
        return cls._meta.permissions

    @classmethod
    def get_queryset(cls):
        return cls._meta.model.objects.all()

    @classmethod
    def get_lookup_field(cls):
        model_class = cls.get_model_class()

        if not cls._meta.lookup_field and model_class:
            return model_class._meta.pk.name

        return cls._meta.lookup_field

    @classmethod
    def get_model_class(cls):
        return cls._meta.model

    @classmethod
    def success_response(cls, instance):
        """Return a success response."""
        return cls(**{cls._meta.return_field_name: instance, "errors": []})

    @classmethod
    def error_response(cls, errors):
        errors = ErrorType.from_errors(errors)
        return cls(errors=errors)

    @classmethod
    def get_model_operations(cls):

        assert (
            "update" in cls._meta.model_operations
            and "create" in cls._meta.model_operations
        ), "model_operations must contain 'create' and/or 'update'"

        return cls._meta.model_operations


class GenericSerializerMutation(BaseMutation):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        lookup_field="pk",
        serializer_class=None,
        _meta=None,
        convert_choices_to_enum=True,
        **options,
    ):
        if not serializer_class:
            raise ImproperlyConfigured(
                "Field serializer_class is required for SerializerMutation"
            )

        if not _meta:
            _meta = ModelMutationOptions(cls)

        _meta.serializer_class = serializer_class
        model = serializer_class.Meta.model

        # serializer = serializer_class()
        # input_fields = fields_for_serializer(
        #     serializer,
        #     list(map(lambda name: name, serializer.fields.keys())),
        #     (),
        #     is_input=True,
        #     convert_choices_to_enum=convert_choices_to_enum,
        #     lookup_field=lookup_field,
        # )
        # input_fields = yank_fields_from_attrs(input_fields, _as=Argument)

        super().__init_subclass_with_meta__(_meta=_meta, model=model, **options)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        serializer = cls.get_serializer(root, info, **data)

        if serializer.is_valid():
            instance = cls.perform_mutate(serializer, info)
            return cls.success_response(instance)
        else:
            return cls.error_response(serializer.errors)

    @classmethod
    def perform_mutate(cls, serializer, info):
        return serializer.save()

    @classmethod
    def get_type_for_model(cls):
        return registry.get_type_for_model(cls._meta.model)

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
                instance = cls.get_object(info, {**{lookup_field: input[lookup_field]}})
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
