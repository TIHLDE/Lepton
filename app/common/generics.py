from rest_framework import permissions


class DRYGraphQLPermissions(permissions.BasePermission):
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
        query_type_name = getattr(view, "_meta", None).class_type

        if query_type_name == "Query":
            action_method_name = "query"
        else:
            action_method_name = "mutation"

        print(action_method_name)

        # Read/Query permissions:
        if action_method_name == "Query":  # request.method in permissions.SAFE_METHODS:
            assert hasattr(model_class, "has_read_permission"), cls._get_error_message(
                model_class, "has_read_permission", action_method_name
            )
            return model_class.has_read_permission(request)
        else:  # Write/Mutation Permissions
            assert hasattr(model_class, "has_write_permission"), cls._get_error_message(
                model_class, "has_write_permission", action_method_name
            )
            return model_class.has_write_permission(request)

    @classmethod
    def has_object_permission(cls, request, view, obj):
        """
        Overrides the standard function and figures out methods to call for object permissions.
        """
        if not cls.object_permissions:
            return True

        model_class = cls._get_model_class(view)

        query_type_name = getattr(view, "_meta", None).class_type
        if query_type_name == "Query":
            action_method_name = "query"
        else:
            action_method_name = "mutation"

        print(action_method_name)

        if action_method_name == "Query":
            assert hasattr(obj, "has_object_read_permission"), cls._get_error_message(
                model_class, "has_object_read_permission", action_method_name
            )
            return obj.has_object_read_permission(request)
        else:
            assert hasattr(obj, "has_object_write_permission"), cls._get_error_message(
                model_class, "has_object_write_permission", action_method_name
            )
            return obj.has_object_write_permission(request)

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
