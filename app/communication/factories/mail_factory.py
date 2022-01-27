import factory
from factory.django import DjangoModelFactory

from app.communication.models.mail import Mail


class MailFactory(DjangoModelFactory):
    class Meta:
        model = Mail

    subject = factory.Sequence(lambda n: f"Mail {n}")
    body = factory.Faker("paragraph", nb_sentences=10)
    sent = False

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        """Add users to the mail: `MailFactory.create(users=(user1, user2, user3))`"""
        if not create or not extracted:
            # Simple build, or nothing to add, do nothing.
            return

        # Add the iterable of users using bulk addition
        self.users.add(*extracted)
