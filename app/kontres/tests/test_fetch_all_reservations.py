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
def create_multiple_reservations(test_user, test_bookable_item):
    for i in range(3):
        Reservation.objects.create(
            author=test_user,
            bookable_item=test_bookable_item,
            start_time=f'2023-10-1{i+1}T10:00:00Z',
            end_time=f'2023-10-1{i+1}T11:00:00Z',
            state='PENDING'
        )


@pytest.mark.django_db
def test_can_fetch_all_reservations(client, create_multiple_reservations, test_user):
    client = APIClient()
    client.force_authenticate(user=test_user)
    response = client.get('/kontres/reservations/', format='json')

    assert response.status_code == 200
    assert len(response.data['reservations']) == 3  # We created 3 reservations

    # Optional: Check that the first reservation in the list is as expected
    first_reservation = Reservation.objects.first()
    assert response.data['reservations'][0]['id'] == first_reservation.id
    assert response.data['reservations'][0]['author'] == first_reservation.author.user_id
    assert response.data['reservations'][0]['bookable_item'] == first_reservation.bookable_item.id
    assert response.data['reservations'][0]['state'] == 'PENDING'




