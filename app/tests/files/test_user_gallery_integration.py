from rest_framework import status

import pytest

from app.files.models.user_gallery import UserGallery
from app.util.test_utils import get_api_client


def _get_user_gallery_url(user_gallery=None):
    return (
        f"/files/user_gallery/{user_gallery.id}/"
        if user_gallery
        else "/files/user_gallery/"
    )


@pytest.mark.django_db
def test_create_user_gallery(admin_user):
    """Tests if an admin can create a gallery"""
    client = get_api_client(user=admin_user)
    url = _get_user_gallery_url()

    assert not UserGallery.has_gallery(admin_user)

    response = client.post(url)

    assert response.status_code == status.HTTP_201_CREATED
    assert UserGallery.objects.filter(author=admin_user).exists()

    user_gallery = UserGallery.objects.get(author=admin_user)
    assert user_gallery.author == admin_user


@pytest.mark.django_db
def test_delete_admin_gallery(admin_user):
    """Tests if an admin can delete their gallery"""
    client = get_api_client(user=admin_user)

    post_url = _get_user_gallery_url()
    response = client.post(post_url)

    assert response.status_code == status.HTTP_201_CREATED

    user_gallery_id = response.data["id"]
    user_gallery = UserGallery.objects.get(id=user_gallery_id)

    delete_url = _get_user_gallery_url(user_gallery)

    response = client.delete(delete_url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not UserGallery.objects.filter(id=user_gallery.id).exists()
