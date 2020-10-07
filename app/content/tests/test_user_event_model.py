from django.test import TestCase

import pytest

from ..factories import (
    EventFactory,
    PriorityFactory,
    RegistrationFactory,
    UserFactory,
)


class TestRegistrationModel(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.event = EventFactory(limit=1)
        self.event.registration_priorities.add(PriorityFactory())

        self.prioritized_user = UserFactory(user_class=1, user_study=1)

        self.not_prioritized_user = UserFactory(user_class=2, user_study=2)
        self.not_prioritized_registration = RegistrationFactory(
            event=self.event, user=self.not_prioritized_user
        )

    def test_swap_users(self):
        """ Test that a non prioritized user is swapped with a prioritized user if the event is full """
        other_user_on_wait = UserFactory(user_class=2, user_study=2)
        RegistrationFactory(event=self.event, user=other_user_on_wait)

        other_user = UserFactory(user_class=1, user_study=1)
        other_registration = RegistrationFactory(event=self.event, user=other_user)

        self.not_prioritized_registration.refresh_from_db()

        assert not other_registration.is_on_wait
        assert self.not_prioritized_registration.is_on_wait

    def test_swap_users_failure(self):
        """ Test that users are not swapped when new user is not prioritized """
        other_user_on_wait = UserFactory(user_class=2, user_study=2)
        RegistrationFactory(event=self.event, user=other_user_on_wait)

        other_user = UserFactory(user_class=2, user_study=2)
        other_registration = RegistrationFactory(event=self.event, user=other_user)

        self.not_prioritized_registration.refresh_from_db()

        assert other_registration.is_on_wait
        assert not self.not_prioritized_registration.is_on_wait

    def test_swap_users_without_priorities(self):
        """ Test that users are not swapped when event does not have any priorities """
        self.event.registration_priorities.clear()

        other_user_on_wait = UserFactory(user_class=2, user_study=2)
        RegistrationFactory(event=self.event, user=other_user_on_wait)

        other_user = UserFactory(user_class=2, user_study=2)
        other_registration = RegistrationFactory(event=self.event, user=other_user)

        self.not_prioritized_registration.refresh_from_db()

        assert other_registration.is_on_wait
        assert not self.not_prioritized_registration.is_on_wait

    def test_swap_users_register_prioritized_when_no_one_to_swap_with_and_event_is_full(
        self,
    ):
        """ Test that a prioritized user is put on wait if there is no one to swap places with and the event is full """

        prioritized_user = UserFactory(user_class=1, user_study=1)
        prioritized_registration = RegistrationFactory(
            event=self.event, user=prioritized_user
        )

        other_prioritized_user = UserFactory(user_class=1, user_study=1)
        other_prioritized_registration = RegistrationFactory(
            event=self.event, user=other_prioritized_user
        )

        self.not_prioritized_registration.refresh_from_db()
        other_prioritized_user.refresh_from_db()

        assert self.not_prioritized_registration.is_on_wait
        assert not prioritized_registration.is_on_wait
        assert other_prioritized_registration.is_on_wait

    def test_should_be_swapped_with_not_prioritized_user(self):
        """ Test that registration is put on list and other registration is put on wait"""
        prioritized_user = RegistrationFactory(user__user_class=1, user__user_study=1)
        prioritized_user.swap_not_prioritized_user(self.not_prioritized_registration)

        assert not prioritized_user.is_on_wait
        assert self.not_prioritized_registration.is_on_wait

    def test_is_prioritized_user_in_priorities(self):
        """ Test that method returns true when user is in a priority """
        prioritized_registration = RegistrationFactory(
            event=self.event, user=self.prioritized_user
        )

        assert prioritized_registration.is_prioritized()

    def test_is_prioritized_user_not_in_priorities(self):
        """ Test that method returns false when user is not in a priority """
        assert not self.not_prioritized_registration.is_prioritized()
