import factory
from factory.django import DjangoModelFactory

from ..models import User


class UserFactory(DjangoModelFactory):

    class Meta:
        model = User

    user_id = factory.LazyAttribute(
        lambda user: f'{user.first_name[:3]}_{user.last_name[3:]}'
    )
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    email = factory.lazy_attribute(
        lambda user: f'{user.user_id}@mail.no'
    )

    user_class = 1
    user_study = 1
