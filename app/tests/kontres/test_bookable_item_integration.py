from rest_framework import status

import pytest

from app.util.test_utils import get_api_client


@pytest.mark.django_db
def test_unauthenticated_request_cannot_create_bookable_item():
    client = get_api_client()
    response = client.post("/kontres/bookable_items/", {"name": "test"}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_delete_bookable_item(admin_user, bookable_item):
    client = get_api_client(user=admin_user)
    response = client.delete(
        f"/kontres/bookable_items/{bookable_item.id}/", format="json"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.data["detail"] == "Gjenstanden ble slettet."


@pytest.mark.django_db
def test_member_cannot_delete_bookable_item(member, bookable_item):
    client = get_api_client(user=member)
    response = client.delete(
        f"/kontres/bookable_items/{bookable_item.id}/", format="json"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_bookable_item_sets_reservation_bookable_item_to_null(
    admin_user, bookable_item, reservation
):
    # Ensure the bookable_item is part of the reservation
    reservation.bookable_item = bookable_item
    reservation.save()

    client = get_api_client(user=admin_user)
    response = client.delete(
        f"/kontres/bookable_items/{bookable_item.id}/", format="json"
    )

    # Refresh the reservation from the database to check the updated state
    reservation.refresh_from_db()

    # The deletion should succeed
    assert response.status_code == 204, "Expected successful deletion of bookable item."

    # After deletion, the reservation's bookable_item should be set to null
    assert (
        reservation.bookable_item is None
    ), "Expected reservation.bookable_item to be set to null after bookable item deletion."


@pytest.mark.django_db
def test_delete_bookable_item_with_invalid_id(admin_user):
    client = get_api_client(user=admin_user)
    invalid_id = 99999
    response = client.delete(f"/kontres/bookable_items/{invalid_id}/", format="json")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_member_cannot_edit_bookable_item(member, bookable_item):
    client = get_api_client(user=member)
    response = client.put("/kontres/bookable_items/", {"name": "test"}, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_edit_bookable_item(admin_user, bookable_item):
    client = get_api_client(user=admin_user)
    response = client.put(
        f"/kontres/bookable_items/{bookable_item.id}/", {"name": "test"}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "test"


@pytest.mark.django_db
def test_get_returns_empty_list_when_no_bookable_items(member):
    client = get_api_client(user=member)
    response = client.get("/kontres/bookable_items/", format="json")

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data == []
    ), "Expected an empty list when there are no bookable items"
