from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet
from django.utils.encoding import force_str
from rest_framework import serializers


class ActionMixin:
    def paginate_response(self, data, serializer, context=None):
        page = self.paginate_queryset(data)
        serializer = serializer(page, many=True, context=context)
        return self.get_paginated_response(serializer.data)


class OrderedModelSerializerMixin:
    order = serializers.IntegerField(read_only=False, required=False)

    def update(self, instance, validated_data):
        self.do_update_order(instance, validated_data)
        return super().update(instance, validated_data)

    @staticmethod
    def do_update_order(instance, data):
        new_order = data.get("order")
        if new_order and getattr(instance, "order") != new_order:
            instance.to(new_order)


class LoggingMethodMixin:
    """
    Adds methods that log changes made to users' data.
    To use this, subclass it and ModelViewSet, and override _get_logging_user(). Ensure
    that the viewset you're mixing this into has `self.model` and `self.serializer_class`
    attributes.
    """

    def log(self, operation, instance):
        if operation == ADDITION:
            action_message = "Created"
        if operation == CHANGE:
            action_message = "Updated"
        if operation == DELETION:
            action_message = "Deleted"
        
        instances = instance if isinstance(instance, list) or isinstance(instance, QuerySet) else [instance]
        for instance in instances:
            message = (
                f'{action_message} {force_str(instance._meta.verbose_name)}s "{force_str(instance)}s".',
            )
            LogEntry.objects.log_action(
                user_id=self.request.user.user_id,
                content_type_id=ContentType.objects.get_for_model(instance).pk,
                object_id=instance.pk,
                object_repr=str(instance),
                action_flag=operation,
                change_message=message,
            )

    def _log_on_create(self, serializer):
        """Log the up-to-date serializer.data."""
        self.log(operation=ADDITION, instance=serializer.instance)

    def _log_on_update(self, serializer):
        """Log data from the updated serializer instance."""
        self.log(operation=CHANGE, instance=serializer.instance)

    def _log_on_destroy(self, instance):
        """Log data from the instance before it gets deleted."""
        self.log(operation=DELETION, instance=instance)


class LoggingViewSetMixin(LoggingMethodMixin):
    """
    A viewset that logs changes made to users' data.
    To use this, subclass it and ModelViewSet, and override _get_logging_user(). Ensure
    that the viewset you're mixing this into has `self.model` and `self.serializer_class`
    attributes.
    If you modify any of the following methods, be sure to call super() or the
    corresponding _log_on_X method:
    - perform_create
    - perform_update
    - perform_destroy
    """

    def perform_create(self, serializer, *args, **kwargs):
        """Create an object and log its data."""
        instance = serializer.save(*args, **kwargs)
        self._log_on_create(serializer)
        return instance

    def perform_update(self, serializer, *args, **kwargs):
        """Update the instance and log the updated data."""
        instance = serializer.save(*args, **kwargs)
        self._log_on_update(serializer)
        return instance

    def perform_destroy(self, instance):
        """Delete the instance and log the deletion."""
        self._log_on_destroy(instance)
        instance.delete()
