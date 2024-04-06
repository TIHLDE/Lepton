from datetime import timedelta

from django.utils import timezone
from rest_framework import status

import pytest

from app.common.enums import AdminGroup
from app.group.factories import GroupFactory
from app.kontres.enums import ReservationStateEnum
from app.kontres.factories.bookable_item_factory import BookableItemFactory
from app.kontres.factories.reservation_factory import ReservationFactory
from app.kontres.models.bookable_item import BookableItem
from app.kontres.models.reservation import Reservation
from app.tests.conftest import _add_user_to_group
from app.util.test_utils import get_api_client


@pytest.mark.django_db
def test_member_can_create_reservation(member, bookable_item):
    client = get_api_client(user=member)

    response = client.post(
        "/kontres/reservations/",
        {
            "bookable_item": bookable_item.id,
            "start_time": "2030-10-10T10:00:00Z",
            "end_time": "2030-10-10T11:00:00Z",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["author_detail"]["user_id"] == str(member.user_id)
    assert response.data["bookable_item_detail"]["id"] == str(bookable_item.id)
    assert response.data["state"] == "PENDING"


@pytest.mark.django_db
def test_member_can_create_reservation_with_alcohol_and_sober_watch(
    member, bookable_item
):
    client = get_api_client(user=member)

    bookable_item.allows_alcohol = True
    bookable_item.save()

    response = client.post(
        "/kontres/reservations/",
        {
            "bookable_item": bookable_item.id,
            "start_time": "2030-10-10T10:00:00Z",
            "end_time": "2030-10-10T11:00:00Z",
            "serves_alcohol": True,
            "sober_watch": member.user_id,
        },
        format="json",
    )

    assert response.status_code == 201, response.data
    assert response.data.get("serves_alcohol") is True
    assert response.data["sober_watch_detail"]["user_id"] == str(member.user_id)


@pytest.mark.django_db
def test_reservation_creation_fails_without_sober_watch(member, bookable_item):
    client = get_api_client(user=member)

    bookable_item.allows_alcohol = True
    bookable_item.save()

    response = client.post(
        "/kontres/reservations/",
        {
            "bookable_item": bookable_item.id,
            "start_time": "2030-10-10T10:00:00Z",
            "end_time": "2030-10-10T11:00:00Z",
            "serves_alcohol": True,
            # Notice the absence of "sober_watch",
        },
        format="json",
    )

    assert response.status_code == 400
    print(response.data)
    expected_error_message = "Du må velge en edruvakt for reservasjonen."
    actual_error_messages = response.data.get("non_field_errors", [])
    assert any(
        expected_error_message in error for error in actual_error_messages
    ), f"Expected specific alcohol agreement validation error: {expected_error_message}"


@pytest.mark.django_db
def test_member_cannot_set_different_author_in_reservation(
    member, bookable_item, sosialen_user
):
    client = get_api_client(user=member)

    # Attempt to create a reservation with a different author specified in the request body
    response = client.post(
        "/kontres/reservations/",
        {
            "author": sosialen_user.user_id,
            "bookable_item": bookable_item.id,
            "start_time": "2030-10-10T10:00:00Z",
            "end_time": "2030-10-10T11:00:00Z",
        },
        format="json",
    )

    # Check that the reservation is created successfully
    assert response.status_code == 201

    # Check that the author of the reservation is actually the requesting user
    assert response.data["author_detail"]["user_id"] == member.user_id
    assert response.data["author_detail"]["user_id"] != "different_user_id"

    # Check other attributes of the reservation
    assert response.data["bookable_item_detail"]["id"] == str(bookable_item.id)
    assert response.data["state"] == "PENDING"


@pytest.mark.django_db
def test_non_tihlde_cannot_create_reservation(user, bookable_item):
    client = get_api_client(user=user)

    response = client.post(
        "/kontres/reservations/",
        {
            "author": user.user_id,
            "bookable_item": bookable_item.id,
            "start_time": "2025-10-10T10:00:00Z",
            "end_time": "2025-10-10T11:00:00Z",
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_creating_reservation_with_past_start_time(member, bookable_item):
    client = get_api_client(user=member)
    past_time = timezone.now() - timezone.timedelta(days=1)
    response = client.post(
        "/kontres/reservations/",
        {
            "author": member.user_id,
            "bookable_item": bookable_item.id,
            "start_time": past_time,
            "end_time": timezone.now(),
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_member_deleting_own_reservation(member, reservation):
    reservation.author = member
    reservation.save()
    client = get_api_client(user=member)
    response = client.delete(f"/kontres/reservations/{reservation.id}/", format="json")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.data["detail"] == "Reservasjonen ble slettet."


@pytest.mark.django_db
def test_member_cannot_update_random_reservation(member, reservation):
    client = get_api_client(user=member)

    new_description = "Updated description"
    response = client.patch(
        f"/kontres/reservations/{reservation.id}/",
        {"description": new_description},
        format="json",
    )

    assert response.status_code == 403
    assert "description" not in response.data


@pytest.mark.django_db
def test_user_cannot_create_confirmed_reservation(bookable_item, member):
    client = get_api_client(user=member)

    # Set start_time to one hour from the current time
    start_time = timezone.now() + timedelta(hours=1)
    # Set end_time to two hours from the current time
    end_time = timezone.now() + timedelta(hours=2)

    response = client.post(
        "/kontres/reservations/",
        {
            "author": member.user_id,
            "bookable_item": bookable_item.id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "state": "CONFIRMED",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["state"] == "PENDING"


@pytest.mark.django_db
def test_user_cannot_create_reservation_with_invalid_date_format(member, bookable_item):
    client = get_api_client(user=member)
    response = client.post(
        "/kontres/reservations/",
        {
            "author": member.user_id,
            "bookable_item": bookable_item.id,
            "start_time": "invalid_date_format",
            "end_time": "2023-10-10T11:00:00Z",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_admin_can_edit_reservation_to_confirmed(reservation, admin_user):
    client = get_api_client(user=admin_user)

    assert reservation.state == ReservationStateEnum.PENDING

    response = client.put(
        f"/kontres/reservations/{reservation.id}/",
        {"state": "CONFIRMED"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["state"] == ReservationStateEnum.CONFIRMED


@pytest.mark.django_db
def test_admin_can_approve_reservation_and_approved_by_is_set(reservation, admin_user):
    client = get_api_client(user=admin_user)
    assert reservation.state == ReservationStateEnum.PENDING
    assert reservation.approved_by is None

    response = client.put(
        f"/kontres/reservations/{reservation.id}/",
        {"state": "CONFIRMED"},
        format="json",
    )

    reservation.refresh_from_db()

    print(response.data)
    assert response.status_code == 200
    assert reservation.state == ReservationStateEnum.CONFIRMED
    assert response.data["approved_by_detail"]["user_id"] == str(
        admin_user.user_id
    ), "The 'approved_by_detail' should contain the correct user ID."


@pytest.mark.django_db
def test_admin_can_edit_reservation_to_cancelled(reservation, admin_user):
    client = get_api_client(user=admin_user)

    response = client.put(
        f"/kontres/reservations/{reservation.id}/",
        {"state": "CANCELLED"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["state"] == "CANCELLED"


@pytest.mark.django_db
def test_updating_reservation_with_valid_times(member, reservation):

    reservation.author = member
    reservation.save()
    client = get_api_client(user=member)

    start_time = timezone.now() + timedelta(hours=1)
    end_time = timezone.now() + timedelta(hours=2)

    response = client.put(
        f"/kontres/reservations/{reservation.id}/",
        {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        },
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK

    # Parse the response times as timezone-aware datetimes
    response_start_time = timezone.datetime.fromisoformat(response.data["start_time"])
    response_end_time = timezone.datetime.fromisoformat(response.data["end_time"])

    # Ensure that the response_end_time is greater than response_start_time
    assert response_end_time > response_start_time


@pytest.mark.django_db
def test_admin_cannot_edit_nonexistent_reservation(admin_user):
    client = get_api_client(user=admin_user)

    nonexistent_uuid = "123e4567-e89b-12d3-a456-426655440000"
    response = client.put(
        f"/kontres/reservations/{nonexistent_uuid}/",
        {"state": "CONFIRMED"},
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_user_can_fetch_all_reservations(reservation, member):
    client = get_api_client(user=member)

    reservations = [reservation]
    for _ in range(2):
        additional_reservation = ReservationFactory()
        reservations.append(additional_reservation)

    response = client.get("/kontres/reservations/", format="json")

    assert response.status_code == 200
    assert len(response.data) == 3

    first_reservation = Reservation.objects.first()
    assert str(response.data[0]["id"]) == str(first_reservation.id)
    assert (
        response.data[0]["author_detail"]["user_id"] == first_reservation.author.user_id
    )
    assert response.data[0]["bookable_item_detail"]["id"] == str(
        first_reservation.bookable_item.id
    )
    assert response.data[0]["state"] == "PENDING"


@pytest.mark.django_db
def test_can_fetch_all_bookable_items(bookable_item, member):
    client = get_api_client(user=member)

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
def test_user_can_fetch_bookable_items_when_none_exist(member):
    client = get_api_client(user=member)
    response = client.get("/kontres/bookable_items/", format="json")

    assert response.status_code == 200, response


@pytest.mark.django_db
def test_can_fetch_single_reservation(reservation, member):
    client = get_api_client(user=member)
    response = client.get(f"/kontres/reservations/{reservation.id}/", format="json")

    assert response.status_code == 200
    assert str(response.data["id"]) == str(reservation.id)
    assert response.data["author_detail"]["user_id"] == reservation.author.user_id
    assert str(response.data["bookable_item_detail"]["id"]) == str(
        reservation.bookable_item.id
    )  # Convert both to string
    assert response.data["state"] == "PENDING"


@pytest.mark.django_db
def test_user_cannot_fetch_nonexistent_reservation(member):
    client = get_api_client(user=member)

    non_existent_uuid = "12345678-1234-5678-1234-567812345678"
    response = client.get(f"/kontres/reservations/{non_existent_uuid}/", format="json")

    assert response.status_code == 404


@pytest.mark.django_db
def test_admin_can_delete_any_reservation(admin_user, reservation):
    client = get_api_client(user=admin_user)
    response = client.delete(
        f"/kontres/reservations/{reservation.id}/",
        format="json",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_user_cannot_edit_others_reservation(user, reservation):
    client = get_api_client(user=user)
    reservation_id = str(reservation.id)
    response = client.put(
        f"/kontres/reservations/{reservation_id}/",
        {"description": "New Description"},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_user_cannot_delete_others_reservation(user, reservation):
    client = get_api_client(user=user)
    reservation_id = str(reservation.id)
    response = client.delete(
        f"/kontres/reservations/{reservation_id}/",
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_cannot_set_invalid_reservation_state(member, reservation):
    client = get_api_client(user=member, group_name=AdminGroup.INDEX)
    reservation_id = str(reservation.id)
    response = client.put(
        f"/kontres/reservations/{reservation_id}/",
        {"state": "INVALID_STATE"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_member_cannot_set_own_reservation_to_invalid_state(member, reservation):
    reservation.author = member
    reservation.save()
    client = get_api_client(user=member)
    reservation_id = str(reservation.id)
    response = client.put(
        f"/kontres/reservations/{reservation_id}/",
        {"state": "INVALID_STATE"},
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_user_cannot_create_reservation_with_end_time_before_start_time(
    member, bookable_item
):
    client = get_api_client(user=member)
    response = client.post(
        "/kontres/reservations/",
        {
            "author": member.user_id,
            "bookable_item": bookable_item.id,
            "start_time": "2025-10-10T12:00:00Z",
            "end_time": "2023-10-10T11:00:00Z",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_user_can_update_own_reservation_details(member, reservation):
    reservation.author = member
    reservation.save()
    client = get_api_client(user=member)
    reservation_id = str(reservation.id)
    new_description = "Updated Description"
    response = client.put(
        f"/kontres/reservations/{reservation_id}/",
        {"description": new_description},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["description"] == new_description


@pytest.mark.django_db
def test_unauthenticated_request_cannot_create_reservation(bookable_item):
    client = get_api_client()
    response = client.post(
        "/kontres/reservations/",
        {
            "bookable_item": bookable_item.id,
            "start_time": "2025-10-10T10:00:00Z",
            "end_time": "2025-10-10T11:00:00Z",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_creating_overlapping_reservation_should_not_work_when_confirmed(
    member, bookable_item, admin_user
):
    # Create a confirmed reservation using the ReservationFactory
    existing_confirmed_reservation = ReservationFactory(
        bookable_item=bookable_item,
        start_time=timezone.now() + timezone.timedelta(hours=1),
        end_time=timezone.now() + timezone.timedelta(hours=2),
        state=ReservationStateEnum.CONFIRMED,  # Set the reservation as confirmed
    )

    # Now attempt to create an overlapping reservation
    client = get_api_client(user=member)
    overlapping_start_time = (
        existing_confirmed_reservation.start_time + timezone.timedelta(minutes=30)
    )
    response = client.post(
        "/kontres/reservations/",
        {
            "author": member.user_id,
            "bookable_item": bookable_item.id,
            "start_time": overlapping_start_time,
            "end_time": existing_confirmed_reservation.end_time
            + timezone.timedelta(hours=1),
            "state": ReservationStateEnum.PENDING,
        },
        format="json",
    )

    # The system should not allow this, as it overlaps with a confirmed reservation
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_updating_to_overlapping_reservation_should_not_work_when_confirmed(
    member, bookable_item, admin_user
):
    # Create two initial reservations, one confirmed and one pending
    confirmed_reservation = ReservationFactory(
        bookable_item=bookable_item,
        start_time=timezone.now() + timezone.timedelta(hours=1),
        end_time=timezone.now() + timezone.timedelta(hours=2),
        state=ReservationStateEnum.CONFIRMED,
    )

    pending_reservation = ReservationFactory(
        bookable_item=bookable_item,
        start_time=confirmed_reservation.start_time
        + timezone.timedelta(minutes=30),  # Overlapping time
        end_time=confirmed_reservation.end_time + timezone.timedelta(minutes=30),
        state=ReservationStateEnum.PENDING,
    )

    # Now attempt to update the pending reservation to confirmed, which should overlap with the confirmed_reservation
    client = get_api_client(user=member)
    response = client.put(
        f"/kontres/reservations/{pending_reservation.id}/",
        {"state": ReservationStateEnum.CONFIRMED},
        format="json",
    )

    # The system should not allow this, as it would overlap with another confirmed reservation
    assert (
        response.status_code == status.HTTP_400_BAD_REQUEST
    ), "Should not update reservation to confirmed due to overlap"


@pytest.mark.django_db
def test_creating_overlapping_reservation_should_work_when_cancelled(
    member, bookable_item, admin_user
):
    existing_confirmed_reservation = ReservationFactory(
        bookable_item=bookable_item,
        start_time=timezone.now() + timezone.timedelta(hours=1),
        end_time=timezone.now() + timezone.timedelta(hours=2),
        state=ReservationStateEnum.CANCELLED,  # Set the reservation as declined
    )

    # Now attempt to create an overlapping reservation
    client = get_api_client(user=member)
    overlapping_start_time = (
        existing_confirmed_reservation.start_time + timezone.timedelta(minutes=30)
    )
    response = client.post(
        "/kontres/reservations/",
        {
            "author": member.user_id,
            "bookable_item": bookable_item.id,
            "start_time": overlapping_start_time,
            "end_time": existing_confirmed_reservation.end_time
            + timezone.timedelta(hours=1),
            "state": ReservationStateEnum.PENDING,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_creating_overlapping_reservation_should_work_when_pending(
    member, bookable_item, admin_user
):
    # Create a confirmed reservation using the ReservationFactory
    existing_confirmed_reservation = ReservationFactory(
        bookable_item=bookable_item,
        start_time=timezone.now() + timezone.timedelta(hours=1),
        end_time=timezone.now() + timezone.timedelta(hours=2),
        state=ReservationStateEnum.PENDING,  # Set the reservation as declined
    )

    # Now attempt to create an overlapping reservation
    client = get_api_client(user=member)
    overlapping_start_time = (
        existing_confirmed_reservation.start_time + timezone.timedelta(minutes=30)
    )
    response = client.post(
        "/kontres/reservations/",
        {
            "author": member.user_id,
            "bookable_item": bookable_item.id,
            "start_time": overlapping_start_time,
            "end_time": existing_confirmed_reservation.end_time
            + timezone.timedelta(hours=1),
            "state": ReservationStateEnum.PENDING,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_retrieve_specific_reservation_within_its_date_range(member, bookable_item):
    client = get_api_client(user=member)

    # Create a reservation with the current time
    reservation = ReservationFactory(
        author=member,
        bookable_item=bookable_item,
        start_time=timezone.now(),
        end_time=timezone.now() + timezone.timedelta(hours=1),
    )

    # Broaden the query time range significantly for debugging
    start_time = reservation.start_time - timezone.timedelta(hours=1)
    end_time = reservation.end_time + timezone.timedelta(hours=1)

    # Format the start and end times in ISO 8601 format
    start_time_iso = start_time.isoformat()
    end_time_iso = end_time.isoformat()

    response = client.get(
        f"/kontres/reservations/?start_date={start_time_iso}&end_date={end_time_iso}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert any(res["id"] == str(reservation.id) for res in response.data)


@pytest.mark.skip
@pytest.mark.django_db
def test_retrieve_subset_of_reservations(member, bookable_item):
    client = get_api_client(user=member)

    # Create three reservations with different times
    # Use current time as a base to ensure consistency
    current_time = timezone.now()

    times = [
        (
            current_time.replace(hour=10, minute=0, second=0, microsecond=0),
            current_time.replace(hour=11, minute=0, second=0, microsecond=0),
        ),
        (
            current_time.replace(hour=10, minute=0, second=0, microsecond=0)
            + timedelta(days=1),
            current_time.replace(hour=11, minute=0, second=0, microsecond=0)
            + timedelta(days=1),
        ),
        (
            current_time.replace(hour=10, minute=0, second=0, microsecond=0)
            + timedelta(days=2),
            current_time.replace(hour=11, minute=0, second=0, microsecond=0)
            + timedelta(days=2),
        ),
    ]

    for start_time, end_time in times:
        client.post(
            "/kontres/reservations/",
            {
                "author": member.user_id,
                "bookable_item": bookable_item.id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            },
            format="json",
        )

    from django.utils.timezone import get_current_timezone

    # Example of formatting the datetime with timezone information
    query_start_date = (
        current_time.replace(hour=9, minute=0, second=0, microsecond=0)
        .astimezone(get_current_timezone())
        .isoformat()
    )

    query_end_date = (
        current_time.replace(
            hour=9, minute=0, second=0, microsecond=0, day=current_time.day + 1
        )
        .astimezone(get_current_timezone())
        .isoformat()
    )

    # Retrieve reservations for the specific date range
    response = client.get(
        f"/kontres/reservations/?start_date={query_start_date}&end_date={query_end_date}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


@pytest.mark.django_db
def test_admin_can_update_confirmed_reservation_state(admin_user, reservation):
    client = get_api_client(user=admin_user)
    # Set the reservation state to CONFIRMED and save
    reservation.state = ReservationStateEnum.CONFIRMED
    reservation.save()

    new_state = "CANCELLED"

    response = client.put(
        f"/kontres/reservations/{reservation.id}/",
        {"state": new_state},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["state"] == new_state


@pytest.mark.django_db
def test_user_cannot_update_confirmed_reservation(member, reservation):
    client = get_api_client(user=member)
    # Confirm the reservation before the test
    reservation.state = ReservationStateEnum.CONFIRMED
    reservation.save()

    response = client.patch(
        f"/kontres/reservations/{reservation.id}/",
        {"description": "Updated description"},
        format="json",
    )

    # Assuming 403 is the status code for a forbidden action
    assert response.status_code == 403


@pytest.mark.django_db
def test_member_can_update_own_reservation(member, reservation):
    client = get_api_client(user=member)

    reservation.author = member
    reservation.save()

    new_description = "Updated description"
    response = client.patch(
        f"/kontres/reservations/{reservation.id}/",
        {"description": new_description},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["description"] == new_description


@pytest.mark.django_db
def test_admin_can_update_details_of_confirmed_reservation(admin_user, reservation):
    client = get_api_client(user=admin_user)

    reservation.state = ReservationStateEnum.CONFIRMED
    reservation.save()

    new_description = "New details after confirmation"
    response = client.patch(
        f"/kontres/reservations/{reservation.id}/",
        {"description": new_description},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["description"] == new_description


@pytest.mark.django_db
def test_user_can_change_reservation_group(member, reservation):
    # Setup: Create two groups and add the user to both
    original_group = GroupFactory()
    new_group = GroupFactory()
    _add_user_to_group(member, original_group)
    _add_user_to_group(member, new_group)

    # Assign the original group to the reservation and save
    reservation.group = original_group
    reservation.author = member
    reservation.save()

    # Prepare the client and attempt to update the reservation's group
    client = get_api_client(user=member)
    reservation_id = str(reservation.id)
    response = client.put(
        f"/kontres/reservations/{reservation_id}/",
        {
            "group": new_group.slug,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK, response.data
    assert response.data["group_detail"]["slug"] == new_group.slug


@pytest.mark.django_db
def test_user_can_create_reservation_for_group(member, bookable_item, group):
    client = get_api_client(user=member)

    _add_user_to_group(member, group)

    response = client.post(
        "/kontres/reservations/",
        {
            "group": group.slug,
            "bookable_item": bookable_item.id,
            "start_time": "2030-10-10T10:00:00Z",
            "end_time": "2030-10-10T11:00:00Z",
        },
        format="json",
    )

    assert response.status_code == 201


@pytest.mark.django_db
def test_user_cannot_create_reservation_for_group_if_not_member_of_group(
    member, bookable_item, group
):
    client = get_api_client(user=member)

    response = client.post(
        "/kontres/reservations/",
        {
            "group": group.slug,
            "bookable_item": bookable_item.id,
            "start_time": "2030-10-10T10:00:00Z",
            "end_time": "2030-10-10T11:00:00Z",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_user_cannot_create_reservation_for_another_group(member, bookable_item):
    client = get_api_client(user=member)

    group1 = GroupFactory()
    group2 = GroupFactory()

    _add_user_to_group(member, group1)

    response = client.post(
        "/kontres/reservations/",
        {
            "group": group2.slug,
            "bookable_item": bookable_item.id,
            "start_time": "2030-10-10T10:00:00Z",
            "end_time": "2030-10-10T11:00:00Z",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_user_can_change_reservation_group_if_state_is_pending(member, reservation):
    original_group = GroupFactory()
    new_group = GroupFactory()
    _add_user_to_group(member, original_group)
    _add_user_to_group(member, new_group)

    reservation.group = original_group
    reservation.author = member
    reservation.save()

    client = get_api_client(user=member)
    reservation_id = str(reservation.id)
    response = client.put(
        f"/kontres/reservations/{reservation_id}/",
        {
            "group": new_group.slug,
        },
        format="json",
    )

    # Verify the response
    assert response.status_code == status.HTTP_200_OK, response.data
    assert response.data["group_detail"]["slug"] == new_group.slug


@pytest.mark.django_db
def test_user_cannot_change_reservation_group_if_state_is_not_pending(
    member, reservation
):
    original_group = GroupFactory()
    new_group = GroupFactory()
    _add_user_to_group(member, original_group)
    _add_user_to_group(member, new_group)

    reservation.group = original_group
    reservation.author = member
    reservation.state = ReservationStateEnum.CONFIRMED
    reservation.save()

    client = get_api_client(user=member)
    reservation_id = str(reservation.id)
    response = client.put(
        f"/kontres/reservations/{reservation_id}/",
        {
            "group": new_group.slug,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_user_can_fetch_own_reservations(member, reservation):
    client = get_api_client(user=member)

    reservation.author = member
    reservation.save()

    response = client.get("/users/me/reservations/")

    assert response.status_code == 200
    assert all(
        reservation["author_detail"]["user_id"] == str(member.user_id)
        for reservation in response.data
    )


@pytest.mark.django_db
def test_user_reservations_endpoint_returns_correct_reservations(
    member, bookable_item, reservation
):
    client = get_api_client(user=member)

    Reservation.objects.bulk_create(
        [
            Reservation(
                author=member,
                bookable_item=bookable_item,
                start_time=f"2030-10-10T1{num}:00:00Z",
                end_time=f"2030-10-10T1{num + 1}:00:00Z",
                description=f"Test reservation {num}",
            )
            for num in range(3)
        ]
    )

    response = client.get("/users/me/reservations/")

    assert response.status_code == 200
    assert len(response.data) == 3

    fixture_reservation_id = str(reservation.id)
    returned_reservation_ids = [res["id"] for res in response.data]
    assert fixture_reservation_id not in returned_reservation_ids


@pytest.mark.django_db
def test_admin_can_fetch_reservations_for_specific_user(
    admin_user, member, bookable_item
):
    client = get_api_client(user=admin_user)

    Reservation.objects.bulk_create(
        [
            Reservation(
                author=member,
                bookable_item=bookable_item,
                start_time=f"2030-10-{10 + num}T10:00:00Z",
                end_time=f"2030-10-{10 + num}T11:00:00Z",
                description=f"Member's reservation {num}",
            )
            for num in range(3)  # Create 3 reservations for the member
        ]
    )

    created_reservations = Reservation.objects.filter(author=member).order_by(
        "start_time"
    )
    created_reservation_ids = {str(res.id) for res in created_reservations}

    response = client.get(f"/kontres/reservations/?user_id={member.user_id}")

    assert response.status_code == 200
    assert len(response.data) == 3

    response_reservation_ids = {res["id"] for res in response.data}

    assert created_reservation_ids == response_reservation_ids


@pytest.mark.django_db
def test_member_cannot_fetch_reservations_for_specific_user(member):
    client = get_api_client(user=member)

    response = client.get(f"/kontres/reservations/?user_id={member.user_id}")

    assert response.status_code == 403
