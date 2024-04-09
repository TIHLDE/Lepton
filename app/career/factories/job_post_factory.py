import factory
from factory.django import DjangoModelFactory

from app.career.models import JobPost


class JobPostFactory(DjangoModelFactory):
    class Meta:
        model = JobPost

    title = factory.Faker("sentence", nb_words=4)
    ingress = factory.Faker("sentence", nb_words=10)
    body = factory.Faker("text")
    location = factory.Faker("city")
    deadline = factory.Faker("date_time")
    company = factory.Faker("company")
    email = factory.Faker("email")
