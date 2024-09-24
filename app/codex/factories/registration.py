import factory
from factory.django import DjangoModelFactory

from app.codex.factories.course import CodexEventFactory
from app.codex.models.registration import CodexEventRegistration
from app.content.factories.user_factory import UserFactory


class CourseRegistrationFactory(DjangoModelFactory):
    class Meta:
        model = CodexEventRegistration

    user = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CodexEventFactory)
    order = 0
