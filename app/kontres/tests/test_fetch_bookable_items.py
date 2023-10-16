import pytest
from rest_framework.test import APIClient
from app.kontres.models.bookable_item import BookableItem


@pytest.fixture()
def test_bookable_item():
    return BookableItem.objects.create(name='Test Item')


@pytest.fixture()
def create_multiple_bookable_items():
    for i in range(3):
        BookableItem.objects.create(
            name=f'Test Item {i+1}'
        )


@pytest.mark.django_db
def test_can_fetch_all_bookable_items(client, create_multiple_bookable_items):
    client = APIClient()
    response = client.get('/kontres/bookable_items/', format='json')

    assert response.status_code == 200
    assert len(response.data) == 3  # We created 3 bookable items

    # Optional: Check that the first bookable item in the list is as expected
    first_bookable_item = BookableItem.objects.first()
    assert str(response.data[0]['id']) == str(first_bookable_item.id)
    assert response.data[0]['name'] == first_bookable_item.name


@pytest.mark.django_db
def test_can_fetch_bookable_items_when_none_exist(client):
    client = APIClient()
    response = client.get('/kontres/bookable_items/', format='json')

    assert response.status_code == 200
    assert len(response.data) == 0  # No bookable items have been created
