import factory
from factory.django import DjangoModelFactory

from ..models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    user_id = factory.Sequence(lambda n: f"User_{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    email = factory.lazy_attribute(lambda user: f"{user.user_id}@mail.no")
