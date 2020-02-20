import pytest
from django.test import TestCase

from ..models import UserEvent
from ..factories import EventFactory, UserFactory, PrioritiesFactory


class TestUserEventModel(TestCase):

    @pytest.mark.django_db
    def setUp(self):
        self.event = EventFactory(limit=1)
        self.event.registration_priorities.add(PrioritiesFactory())
        self.user = UserFactory(user_class=2, user_study=2)
        self.user_event = UserEvent.objects.create(event=self.event, user=self.user)

    def test_swap_users(self):
        """ Test that a non prioritized user is swapped with a prioritized user if the event is full """
        other_user_on_wait = UserFactory(user_class=2, user_study=2)
        UserEvent.objects.create(event=self.event, user=other_user_on_wait)

        other_user = UserFactory(user_class=1, user_study=1)
        other_user_event = UserEvent.objects.create(event=self.event, user=other_user)

        self.user_event.refresh_from_db()

        assert not other_user_event.is_on_wait
        assert self.user_event.is_on_wait

    def test_swap_users_failure(self):
        """ Test that users are not swapped when new user is not prioritized """
        other_user_on_wait = UserFactory(user_class=2, user_study=2)
        UserEvent.objects.create(event=self.event, user=other_user_on_wait)

        other_user = UserFactory(user_class=2, user_study=2)
        other_user_event = UserEvent.objects.create(event=self.event, user=other_user)

        self.user_event.refresh_from_db()

        assert other_user_event.is_on_wait
        assert not self.user_event.is_on_wait

    def test_swap_users_without_priorities(self):
        """ Test that users are not swapped when event does not have any priorities """
        self.event.registration_priorities.clear()

        other_user_on_wait = UserFactory(user_class=2, user_study=2)
        UserEvent.objects.create(event=self.event, user=other_user_on_wait)

        other_user = UserFactory(user_class=2, user_study=2)
        other_user_event = UserEvent.objects.create(event=self.event, user=other_user)

        self.user_event.refresh_from_db()

        assert other_user_event.is_on_wait
        assert not self.user_event.is_on_wait

