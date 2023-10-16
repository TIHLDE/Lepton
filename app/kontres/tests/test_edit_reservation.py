from rest_framework.test import APIClient

import pytest

from app.content.models import User
from app.kontres.models.bookable_item import BookableItem
from app.kontres.models.reservation import Reservation


@pytest.fixture()
def test_user():
    return User.objects.create(user_id="test_user")


@pytest.fixture()
def test_bookable_item():
    return BookableItem.objects.create(name="Test Item")


@pytest.fixture()
def create_valid_reservation_for_editing(test_user, test_bookable_item):
    reservation = Reservation.objects.create(
        author=test_user,
        bookable_item=test_bookable_item,
        start_time="2023-10-10T10:00:00Z",
        end_time="2023-10-10T11:00:00Z",
        state="PENDING",
    )
    return reservation


@pytest.mark.django_db
def test_admin_can_edit_reservation(create_valid_reservation_for_editing, test_user):
    client = APIClient()
    client.force_authenticate(user=test_user)

    reservation_id = str(create_valid_reservation_for_editing.id)
    response = client.put(
        f"/kontres/reservations/{reservation_id}/",
        {"state": "CONFIRMED"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["state"] == "CONFIRMED"


@pytest.mark.django_db
def test_user_cannot_edit_nonexistent_reservation(test_user):
    client = APIClient()
    client.force_authenticate(user=test_user)

    nonexistent_uuid = "123e4567-e89b-12d3-a456-426655440000"
    response = client.put(
        f"/kontres/reservations/{nonexistent_uuid}/",
        {"state": "CONFIRMED"},
        format="json",
    )

    assert response.status_code == 404
