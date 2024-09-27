import factory
from factory.django import DjangoModelFactory

from app.codex.factories.event import CodexEventFactory
from app.codex.models.registration import CodexEventRegistration
from app.content.factories.user_factory import UserFactory


class CodexEventRegistrationFactory(DjangoModelFactory):
    class Meta:
        model = CodexEventRegistration

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(CodexEventFactory)
    order = 0
