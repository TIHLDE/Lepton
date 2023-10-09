import pytest
from app.content.models import User
from rest_framework.test import APIClient
from app.kontres.models.bookable_item import BookableItem
from app.kontres.models.reservation import Reservation


@pytest.fixture()
def test_user():
    return User.objects.create(user_id='test_user')


@pytest.fixture()
def test_bookable_item():
    return BookableItem.objects.create(name='Test Item')


@pytest.fixture()
def create_valid_reservation_for_editing(test_user, test_bookable_item):
    reservation = Reservation.objects.create(
        author=test_user,
        bookable_item=test_bookable_item,
        start_time='2023-10-10T10:00:00Z',
        end_time='2023-10-10T11:00:00Z',
        state='PENDING'
    )
    return reservation


@pytest.mark.django_db
def test_can_fetch_single_reservation(client, create_valid_reservation_for_editing):
    reservation = create_valid_reservation_for_editing
    client = APIClient()
    client.force_authenticate(user=reservation.author)
    response = client.get(f'/kontres/reservations/{reservation.id}/', format='json')

    assert response.status_code == 200
    assert str(response.data['id']) == str(reservation.id)  # Convert both to string
    assert response.data['author'] == reservation.author.user_id
    assert str(response.data['bookable_item']) == str(reservation.bookable_item.id)  # Convert both to string
    assert response.data['state'] == 'PENDING'


@pytest.mark.django_db
def test_user_cannot_fetch_nonexistent_reservation(test_user):
    client = APIClient()
    client.force_authenticate(user=test_user)

    non_existent_uuid = '12345678-1234-5678-1234-567812345678'
    response = client.get(f'/kontres/reservations/{non_existent_uuid}/', format='json')

    assert response.status_code == 404
