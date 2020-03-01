import factory.django

from ..models import User


class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = User

    user_id = factory.Faker('first_name')
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    email = factory.lazy_attribute(
        lambda user: f'{user.user_id}@mail.no'
    )

    user_class = 1
    user_study = 1
