from datetime import timedelta

from django.utils import timezone

import factory
from factory.django import DjangoModelFactory

from app.codex.models.course import Course


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = Course

    title = factory.Sequence(lambda n: f"Course {n}")
    description = factory.Faker("text")
    start_date = timezone.now() + timedelta(days=10)
    end_date = timezone.now() + timedelta(days=11)

    start_registration_at = timezone.now() - timedelta(days=1)
    end_registration_at = timezone.now() + timedelta(days=9)
    sign_off_deadline = timezone.now() + timedelta(days=8)
