import factory
from factory.django import DjangoModelFactory

from app.content.factories.event_factory import EventFactory
from app.content.models.priority_pool import PriorityPool


class PriorityPoolFactory(DjangoModelFactory):
    class Meta:
        model = PriorityPool

    event = factory.SubFactory(EventFactory)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for group in extracted:
                self.groups.add(group)
