from rest_framework import permissions
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.generics import get_object_or_404

import graphene
from graphene_django.types import ErrorType


class DRYGraphQLPermissions(
    permissions.BasePermission
):  # TODO: sjekk ut denne for auth middleware: https://github.com/graphql-python/graphene-django/issues/345#issuecomment-572834490
    """
    This class can be used directly by a DRF view or can be used as a
    base class for a custom permissions class. This class helps to organize
    permission methods that are defined on the model class that is defined
    on the serializer for this view.

    DRYPermissions will call action based methods on the model in the following order:
    1) Global permissions (format has_{action}_permission):
        1a) specific action permissions (e.g. has_retrieve_permission)
        1b) general action permissions  (e.g. has_read_permission)
    2) Object permissions for a specific object (format has_object_{action}_permission):
        2a) specific action permissions (e.g. has_object_retrieve_permission)
        2b) general action permissions  (e.g. has_object_read_permission)

    If either of the specific permissions do not exist, the DRYPermissions will
    simply check the general permission.
    If any step in this process returns False then the checks stop there and
    throw a permission denied. If there is a "specific action" step then the
    "generic step" is skipped. In order to have permission there must be True returned
    from both the Global and Object permissions categories, unless the global_permissions
    or object_permissions attributes are set to False.

    Specific action permissions take their name from the action name,
    which is either DRF defined (list, retrieve, update, destroy, create)
    or developer defined for custom actions created using @list_route or @detail_route.

    Options that may be overridden when using as a base class:
    global_permissions: If set to False then global permissions are not checked.
    object_permissions: If set to False then object permissions are not checked.
    partial_update_is_update: If set to False then specific permissions for
        partial_update can be set, otherwise they will just use update permissions.

    """

    global_permissions = True
    object_permissions = True
    partial_update_is_update = True

    @classmethod
    def has_permission(cls, request, view):
        """
        Overrides the standard function and figures out methods to call for global permissions.
        """
        if not cls.global_permissions:
            return True

        model_class = cls._get_model_class(view)

        assert model_class is not None, (
            "global_permissions set to true without a model "
            "queryset for '%s'" % view.__class__.__name__
        )

        # TODO: this does not work well
        operation = request.operation.operation

        if operation == "query":  # request.method in permissions.SAFE_METHODS:
            assert hasattr(model_class, "has_read_permission"), cls._get_error_message(
                model_class, "has_read_permission", operation
            )
            return model_class.has_read_permission(request.context)
        else:  # Write/Mutation Permissions
            assert hasattr(model_class, "has_write_permission"), cls._get_error_message(
                model_class, "has_write_permission", operation
            )
            return model_class.has_write_permission(request.context)

    @classmethod
    def has_object_permission(cls, request, view, obj):
        """
        Overrides the standard function and figures out methods to call for object permissions.
        """
        if not cls.object_permissions:
            return True

        model_class = cls._get_model_class(view)

        print("OPERATION: ", request.operation.operation)
        operation = request.operation.operation

        if operation == "query":
            assert hasattr(obj, "has_object_read_permission"), cls._get_error_message(
                model_class, "has_object_read_permission", operation
            )
            return obj.has_object_read_permission(request.context)
        else:
            assert hasattr(obj, "has_object_write_permission"), cls._get_error_message(
                model_class, "has_object_write_permission", operation
            )
            return obj.has_object_write_permission(request.context)

    @classmethod
    def _get_model_class(cls, view):
        queryset = view.get_queryset()  # TODO: assert queryset is not None
        return queryset.model

    @classmethod
    def _get_error_message(cls, model_class, method_name, action_method_name):
        """
        Get assertion error message depending if there are actions permissions methods defined.
        """
        if action_method_name:
            return "'{}' does not have '{}' or '{}' defined.".format(
                model_class, method_name, action_method_name
            )
        else:
            return "'{}' does not have '{}' defined.".format(model_class, method_name)


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


class GenericSerializerMutation(GenericQuery):
    serializer_class = None
    lookup_field = "pk"
    model_operations = ["create", "update"]

    errors = graphene.List(
        ErrorType, description="May contain more than one error for same field."
    )

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
        assert cls.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method." % cls.__class__.__name__
        )

        return cls.serializer_class

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
        model_class = cls.get_serializer_class

        if not cls.lookup_field and model_class:
            return model_class._meta.pk.name

        return cls.lookup_field

    @classmethod
    def get_model_class(cls):
        return cls.serializer_class.Meta.model

    @classmethod
    def get_model_operations(cls):

        assert (
            "update" in cls.model_operations and "create" in cls.model_operations
        ), "model_operations must contain 'create' and/or 'update'"

        return cls.model_operations
