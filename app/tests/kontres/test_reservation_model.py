from django.db.utils import IntegrityError
from django.utils import timezone

import pytest

from app.content.models import User
from app.kontres.models.bookable_item import BookableItem
from app.kontres.models.reservation import Reservation, ReservationStateEnum


@pytest.fixture()
def reservation():
    user = User.objects.create(user_id="test_user")
    bookable_item = BookableItem.objects.create(name="Test Item")
    return Reservation.objects.create(
        author=user,
        bookable_item=bookable_item,
        start_time=timezone.now(),
        end_time=timezone.now() + timezone.timedelta(hours=1),
    )


@pytest.mark.django_db
def test_reservation_defaults_to_pending(reservation):
    assert reservation.state == ReservationStateEnum.PENDING


@pytest.mark.django_db
def test_reservation_start_and_end_time():
    user = User.objects.create(user_id="test_user", email="test@test.com")
    bookable_item = BookableItem.objects.create(name="Test Item")
    start_time = timezone.now()
    end_time = start_time + timezone.timedelta(hours=1)
    reservation = Reservation.objects.create(
        author=user,
        bookable_item=bookable_item,
        start_time=start_time,
        end_time=end_time,
    )
    assert reservation.start_time == start_time
    assert reservation.end_time == end_time


@pytest.mark.django_db
def test_state_transitions(reservation):
    """Should correctly transition between states."""

    # Start with a PENDING reservation
    assert reservation.state == ReservationStateEnum.PENDING

    # Move to CONFIRMED
    reservation.state = ReservationStateEnum.CONFIRMED
    reservation.save()
    assert reservation.state == ReservationStateEnum.CONFIRMED

    # Move to CANCELLED
    reservation.state = ReservationStateEnum.CANCELLED
    reservation.save()
    assert reservation.state == ReservationStateEnum.CANCELLED


@pytest.mark.django_db
def test_reservation_requires_bookable_item():
    with pytest.raises(IntegrityError):
        user = User.objects.create(user_id="test_user", email="test@test.com")
        Reservation.objects.create(
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            author=user,
        )


@pytest.mark.django_db
def test_created_at_field():
    user = User.objects.create(user_id="test_user", email="test@test.com")
    bookable_item = BookableItem.objects.create(name="Test Item")
    reservation = Reservation.objects.create(
        author=user,
        bookable_item=bookable_item,
        start_time=timezone.now(),
        end_time=timezone.now() + timezone.timedelta(hours=1),
    )
    assert reservation.created_at is not None


@pytest.mark.django_db
def test_multiple_reservations():
    user1 = User.objects.create(user_id="test_user_1", email="test1@test.com")
    user2 = User.objects.create(user_id="test_user_2", email="test2@test.com")
    bookable_item = BookableItem.objects.create(name="Test Item")
    reservation1 = Reservation.objects.create(
        author=user1,
        bookable_item=bookable_item,
        start_time=timezone.now(),
        end_time=timezone.now() + timezone.timedelta(hours=1),
    )
    reservation2 = Reservation.objects.create(
        author=user2,
        bookable_item=bookable_item,
        start_time=timezone.now(),
        end_time=timezone.now() + timezone.timedelta(hours=1),
    )
    assert reservation1 is not None
    assert reservation2 is not None


@pytest.mark.django_db
def test_reservation_requires_author():
    with pytest.raises(IntegrityError):
        bookable_item = BookableItem.objects.create(name="Test Item")
        Reservation.objects.create(
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            bookable_item=bookable_item,
        )


@pytest.mark.django_db
def test_reservation_with_group(group):
    user = User.objects.create(user_id="test_user")
    bookable_item = BookableItem.objects.create(name="Test Item")
    reservation = Reservation.objects.create(
        author=user,
        bookable_item=bookable_item,
        start_time=timezone.now(),
        end_time=timezone.now() + timezone.timedelta(hours=1),
        group=group,
    )
    assert reservation.group == group
