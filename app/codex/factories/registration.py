import factory
from factory.django import DjangoModelFactory

from app.codex.factories.course import CourseFactory
from app.codex.models.registration import CourseRegistration
from app.content.factories.user_factory import UserFactory


class CourseRegistrationFactory(DjangoModelFactory):
    class Meta:
        model = CourseRegistration

    user = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)
    order = 0
