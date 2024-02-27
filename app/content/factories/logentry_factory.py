from django.contrib.admin.models import LogEntry
from django.utils import timezone

import factory
from factory.django import DjangoModelFactory

from app.content.factories.user_factory import UserFactory


class LogEntryFactory(DjangoModelFactory):
    class Meta:
        model = LogEntry

    action_time = timezone.now()
    user = factory.SubFactory(UserFactory)
    content_type = None
    object_id = 1
    object_repr = "Test"
    action_flag = 1
