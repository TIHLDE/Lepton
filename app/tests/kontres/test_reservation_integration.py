from rest_framework import status

import pytest

from app.common.enums import AdminGroup
from app.kontres.factories.bookable_item_factory import BookableItemFactory
from app.kontres.factories.reservation_factory import ReservationFactory
from app.kontres.models.bookable_item import BookableItem
from app.kontres.models.reservation import Reservation
from app.util.test_utils import get_api_client


@pytest.mark.django_db
def test_user_can_create_reservation(user, bookable_item):
    client = get_api_client(user=user)

    response = client.post(
        "/kontres/reservations/",
        {
            "author": user.user_id,
            "bookable_item": bookable_item.id,
            "start_time": "2023-10-10T10:00:00Z",
            "end_time": "2023-10-10T11:00:00Z",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["author"] == user.user_id
    assert response.data["bookable_item"] == bookable_item.id
    assert response.data["state"] == "PENDING"


@pytest.mark.django_db
def test_anonymous_cannot_create_reservation(default_client, bookable_item):

    client = default_client
    response = client.post(
        "/kontres/reservations/",
        {
            "bookable_item": bookable_item.id,
            "start_time": "2023-10-10T10:00:00Z",
            "end_time": "2023-10-10T11:00:00Z",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_user_cannot_create_confirmed_reservation(bookable_item, member):
    client = get_api_client(user=member)

    response = client.post(
        "/kontres/reservations/",
        {
            "author": member.user_id,
            "bookable_item": bookable_item.id,
            "start_time": "2023-10-10T10:00:00Z",
            "end_time": "2023-10-10T11:00:00Z",
            "state": "CONFIRMED",
        },
        format="json",
    )

    assert response.data["state"] == "PENDING"


@pytest.mark.django_db
def test_user_cannot_create_reservation_without_author(client, bookable_item):
    response = client.post(
        "/kontres/reservations/",
        {
            "bookable_item_id": bookable_item.id,
            "start_time": "2023-10-10T10:00:00Z",
            "end_time": "2023-10-10T11:00:00Z",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_user_cannot_create_reservation_with_invalid_date_format(
    client, user, bookable_item
):
    response = client.post(
        "/kontres/reservations/",
        {
            "author": user.user_id,
            "bookable_item_id": bookable_item.id,
            "start_time": "invalid_date_format",
            "end_time": "2023-10-10T11:00:00Z",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_admin_can_edit_reservation(reservation, user):
    client = get_api_client(user=user, group_name=AdminGroup.HS)

    reservation_id = str(reservation.id)
    response = client.put(
        f"/kontres/reservations/{reservation_id}/",
        {"state": "CONFIRMED"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["state"] == "CONFIRMED"


@pytest.mark.django_db
def test_edit_as_user(reservation, user):
    client = get_api_client(user=user)

    reservation_id = str(reservation.id)
    response = client.put(
        f"/kontres/reservations/{reservation_id}/",
        {"state": "CONFIRMED"},
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_cannot_edit_nonexistent_reservation(user):
    client = get_api_client(user=user, group_name=AdminGroup.HS)

    nonexistent_uuid = "123e4567-e89b-12d3-a456-426655440000"
    response = client.put(
        f"/kontres/reservations/{nonexistent_uuid}/",
        {"state": "CONFIRMED"},
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_user_can_fetch_all_reservations(reservation, user):
    client = get_api_client(user=user)

    reservations = [reservation]
    for _ in range(2):
        additional_reservation = ReservationFactory()
        reservations.append(additional_reservation)

    response = client.get("/kontres/reservations/", format="json")

    assert response.status_code == 200
    assert len(response.data["reservations"]) == 3

    first_reservation = Reservation.objects.first()
    assert str(response.data["reservations"][0]["id"]) == str(first_reservation.id)
    assert (
        response.data["reservations"][0]["author"] == first_reservation.author.user_id
    )
    assert (
        response.data["reservations"][0]["bookable_item"]
        == first_reservation.bookable_item.id
    )
    assert response.data["reservations"][0]["state"] == "PENDING"


@pytest.mark.django_db
def test_can_fetch_all_bookable_items(bookable_item, user):
    client = get_api_client(user=user)

    bookable_items = [bookable_item]
    for _ in range(2):
        additional_bookable_item = BookableItemFactory()
        bookable_items.append(additional_bookable_item)

    response = client.get("/kontres/bookable_items/", format="json")

    assert response.status_code == 200
    assert len(response.data) == 3

    first_bookable_item = BookableItem.objects.first()
    assert str(response.data[0]["id"]) == str(first_bookable_item.id)
    assert response.data[0]["name"] == first_bookable_item.name


@pytest.mark.django_db
def test_can_fetch_bookable_items_when_none_exist(user):
    client = get_api_client(user=user)
    response = client.get("/kontres/bookable_items/", format="json")

    assert response.status_code == 200
    assert len(response.data) == 0


@pytest.mark.django_db
def test_can_fetch_single_reservation(reservation, user):
    client = get_api_client(user=user)
    response = client.get(f"/kontres/reservations/{reservation.id}/", format="json")

    assert response.status_code == 200
    assert str(response.data["id"]) == str(reservation.id)
    assert response.data["author"] == reservation.author.user_id
    assert str(response.data["bookable_item"]) == str(
        reservation.bookable_item.id
    )  # Convert both to string
    assert response.data["state"] == "PENDING"


@pytest.mark.django_db
def test_user_cannot_fetch_nonexistent_reservation(user):
    client = get_api_client(user=user)

    non_existent_uuid = "12345678-1234-5678-1234-567812345678"
    response = client.get(f"/kontres/reservations/{non_existent_uuid}/", format="json")

    assert response.status_code == 404
