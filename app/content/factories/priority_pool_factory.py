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
        if not create or not extracted:
            # Simple build, do nothing.
            return

        # Add the iterable of groups using bulk addition
        self.groups.add(*extracted)
