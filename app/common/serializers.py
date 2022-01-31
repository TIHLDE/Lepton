from django.contrib.admin.models import ADDITION, CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_str
from rest_framework import serializers


class LoggerSerializer(serializers.ModelSerializer):
    """
    Creates a log entry of the action performed by
    the current user on the related instance.
    """

    def create(self, validated_data):
        user = self._get_user()
        instance = super().create(validated_data)

        if instance.pk:
            _log_action(
                instance=instance, user=user, action="Added", action_flag=ADDITION
            )

        return instance

    def _get_user(self):
        return self.context["request"].user

    def update(self, instance, validated_data):
        user = self._get_user()
        instance = super().update(instance, validated_data)

        if instance.pk:
            _log_action(
                instance=instance, user=user, action="Updated", action_flag=CHANGE
            )

        return instance

    def delete(self, instance, validated_data):
        user = self._get_user()
        instance = super().delete(instance, validated_data)

        if instance.pk:
            _log_action(
                instance=instance, user=user, action="Deleted", action_flag=CHANGE
            )

        return instance


def _log_action(instance, user, action, action_flag):
    message = (
        f'{action} {force_str(instance._meta.verbose_name)}s "{force_str(instance)}s".',
    )
    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=ContentType.objects.get_for_model(instance).pk,
        object_id=instance.pk,
        object_repr=force_str(instance),
        action_flag=action_flag,
        change_message=message,
    )


class BaseModelSerializer(LoggerSerializer):
    pass
