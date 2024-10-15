import pytest
from rest_framework import status

from app.files.models.user_gallery import UserGallery
from app.files.serializers.user_gallery import UserGallerySerializer
from app.tests.utils import get_api_client


@pytest.mark.django_db
def test_create_user_gallery(admin_user):
    """Tests if an admin user can create a new user gallery."""
    
    client = get_api_client(user=admin_user)
    
    url = '/user_gallery/' 
    
    data = {
        "author": admin_user.id 
    }

    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
