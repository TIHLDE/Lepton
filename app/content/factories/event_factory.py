from datetime import datetime, timedelta
from django.utils import timezone
import factory.django

from ..models import Event
from .priorities_factory import PrioritiesFactory


class EventFactory(factory.DjangoModelFactory):

    class Meta:
        model = Event

    title = 'Test Event'
    start_date = timezone.now() + timedelta(days=10)
    end_date = timezone.now() + timedelta(days=11)
    sign_up = True

    start_registration_at = timezone.now() - timedelta(days=1)
    end_registration_at = timezone.now() + timedelta(days=9)
    sign_off_deadline = timezone.now() + timedelta(days=8)

    @factory.post_generation
    def registration_priorities(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for priority in extracted:
                self.registration_priorities.add(priority)
