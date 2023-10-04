import pytest
from app.content.models import User
from rest_framework.test import APIClient
from app.kontres.models.bookable_item import BookableItem


@pytest.fixture()
def test_user():
    return User.objects.create(user_id='test_user')


@pytest.fixture()
def test_bookable_item():
    return BookableItem.objects.create(name='Test Item')


@pytest.fixture()
def create_valid_reservation(client, test_user, test_bookable_item):
    response = client.post(f'/kontres/create_reservation/?bookable_item={test_bookable_item.id}', {
        'author': test_user.user_id,
        'start_time': '2023-10-10T10:00:00Z',
        'end_time': '2023-10-10T11:00:00Z',
    }, format='json')
    return response


@pytest.mark.django_db
def test_user_can_create_reservation(test_user, test_bookable_item):
    client = APIClient()
    client.force_authenticate(user=test_user)

    response = client.post(f'/kontres/create_reservation/?bookable_item={test_bookable_item.id}', {
        'author': test_user.user_id,
        'start_time': '2023-10-10T10:00:00Z',
        'end_time': '2023-10-10T11:00:00Z',
    }, format='json')

    assert response.status_code == 201
    assert response.data['author'] == test_user.user_id
    assert response.data['bookable_item']['id'] == test_bookable_item.id
    assert response.data['state'] == 'PENDING'


@pytest.mark.django_db
def test_user_cannot_create_reservation_without_author(client, test_bookable_item):
    response = client.post(f'/kontres/create_reservation/?bookable_item={test_bookable_item.id}', {
        'start_time': '2023-10-10T10:00:00Z',
        'end_time': '2023-10-10T11:00:00Z',
    }, format='json')

    assert response.status_code == 400


@pytest.mark.django_db
def test_user_cannot_create_reservation_with_invalid_date_format(client, test_user, test_bookable_item):
    response = client.post(f'/kontres/create_reservation/?bookable_item={test_bookable_item.id}', {
        'author': test_user.user_id,
        'start_time': 'invalid_date_format',
        'end_time': '2023-10-10T11:00:00Z',
    }, format='json')

    assert response.status_code == 400
