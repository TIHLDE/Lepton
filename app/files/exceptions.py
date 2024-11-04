from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError

from app.constants import MAX_GALLERY_SIZE


class APINoGalleryFoundForUser(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Ingen galleri ble funnet for brukeren."


class NoGalleryFoundForUser(ValidationError):
    default_detail = "Ingen galleri ble funnet for brukeren."


class APIGalleryIsFull(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = f"Galleriet er fullt med {MAX_GALLERY_SIZE} filer."


class GalleryIsFull(ValidationError):
    default_detail = f"Galleriet er fullt med {MAX_GALLERY_SIZE} filer."
