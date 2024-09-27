from datetime import timedelta

from django.utils import timezone

import factory
from factory.django import DjangoModelFactory

from app.codex.models.event import CodexEvent


class CodexEventFactory(DjangoModelFactory):
    class Meta:
        model = CodexEvent

    title = factory.Sequence(lambda n: f"Event {n}")
    description = factory.Faker("text")
    start_date = timezone.now() + timedelta(days=10)

    start_registration_at = timezone.now() - timedelta(days=1)
    end_registration_at = timezone.now() + timedelta(days=9)
