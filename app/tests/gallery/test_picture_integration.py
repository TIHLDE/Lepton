from rest_framework import status

import pytest

from app.gallery.factories.picture_factory import PictureFactory
from app.gallery.views.picture import PictureViewSet
from app.util.test_utils import get_api_client
from app.common.enums import AdminGroup
from app.common.enums import Groups

pytestmark = pytest.mark.django_db
API_PICTURE_BASE_URL = "/picture/"

@pytest.mark.django_db
@pytest.mark.parametrize(
    ("group_name", "expected_status_code"),
    [
        (AdminGroup.HS, status.HTTP_200_OK),
        (AdminGroup.INDEX, status.HTTP_200_OK),
        (AdminGroup.NOK, status.HTTP_200_OK),
        (AdminGroup.SOSIALEN, status.HTTP_200_OK),
        (AdminGroup.PROMO, status.HTTP_200_OK),
        (Groups.TIHLDE, status.HTTP_403_FORBIDDEN),
    ],
)
def test_that_only_admin_has_writing_acsess_for_picture(member, group_name, expected_status_code):
    """A admin user can create a picture"""
    client = get_api_client(user=member, group_name=group_name)
    picture = PictureFactory()
    response = client.create(API_PICTURE_BASE_URL, picture)

    assert response.status_code == expected_status_code