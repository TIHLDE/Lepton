from django.test import TestCase

import pytest

from ..factories import (
    EventFactory,
    PriorityFactory,
    UserEventFactory,
    UserFactory,
)


class TestUserEventModel(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.event = EventFactory(limit=1)
        self.event.registration_priorities.add(PriorityFactory())

        self.prioritized_user = UserFactory(user_class=1, user_study=1)

        self.not_prioritized_user = UserFactory(user_class=2, user_study=2)
        self.not_prioritized_user_event = UserEventFactory(
            event=self.event, user=self.not_prioritized_user
        )

    def test_swap_users(self):
        """ Test that a non prioritized user is swapped with a prioritized user if the event is full """
        other_user_on_wait = UserFactory(user_class=2, user_study=2)
        UserEventFactory(event=self.event, user=other_user_on_wait)

        other_user = UserFactory(user_class=1, user_study=1)
        other_user_event = UserEventFactory(event=self.event, user=other_user)

        self.not_prioritized_user_event.refresh_from_db()

        assert not other_user_event.is_on_wait
        assert self.not_prioritized_user_event.is_on_wait

    def test_swap_users_failure(self):
        """ Test that users are not swapped when new user is not prioritized """
        other_user_on_wait = UserFactory(user_class=2, user_study=2)
        UserEventFactory(event=self.event, user=other_user_on_wait)

        other_user = UserFactory(user_class=2, user_study=2)
        other_user_event = UserEventFactory(event=self.event, user=other_user)

        self.not_prioritized_user_event.refresh_from_db()

        assert other_user_event.is_on_wait
        assert not self.not_prioritized_user_event.is_on_wait

    def test_swap_users_without_priorities(self):
        """ Test that users are not swapped when event does not have any priorities """
        self.event.registration_priorities.clear()

        other_user_on_wait = UserFactory(user_class=2, user_study=2)
        UserEventFactory(event=self.event, user=other_user_on_wait)

        other_user = UserFactory(user_class=2, user_study=2)
        other_user_event = UserEventFactory(event=self.event, user=other_user)

        self.not_prioritized_user_event.refresh_from_db()

        assert other_user_event.is_on_wait
        assert not self.not_prioritized_user_event.is_on_wait

    def test_swap_users_register_prioritized_when_no_one_to_swap_with_and_event_is_full(
        self,
    ):
        """ Test that a prioritized user is put on wait if there is no one to swap places with and the event is full """

        prioritized_user = UserFactory(user_class=1, user_study=1)
        prioritized_user_event = UserEventFactory(
            event=self.event, user=prioritized_user
        )

        other_prioritized_user = UserFactory(user_class=1, user_study=1)
        other_prioritized_user_event = UserEventFactory(
            event=self.event, user=other_prioritized_user
        )

        self.not_prioritized_user_event.refresh_from_db()
        other_prioritized_user.refresh_from_db()

        assert self.not_prioritized_user_event.is_on_wait
        assert not prioritized_user_event.is_on_wait
        assert other_prioritized_user_event.is_on_wait

    def test_should_be_swapped_with_not_prioritized_user(self):
        """ Test that user_event is put on list and other user_event is put on wait"""
        prioritized_user = UserEventFactory(user__user_class=1, user__user_study=1)
        prioritized_user.swap_not_prioritized_user(self.not_prioritized_user_event)

        assert not prioritized_user.is_on_wait
        assert self.not_prioritized_user_event.is_on_wait

    def test_is_prioritized_user_in_priorities(self):
        """ Test that method returns true when user is in a priority """
        prioritized_user_event = UserEventFactory(
            event=self.event, user=self.prioritized_user
        )

        assert prioritized_user_event.is_prioritized()

    def test_is_prioritized_user_not_in_priorities(self):
        """ Test that method returns false when user is not in a priority """
        assert not self.not_prioritized_user_event.is_prioritized()
