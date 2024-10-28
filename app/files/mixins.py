from app.files.exceptions import (
    NoGalleryFoundForUser,
    APINoGalleryFoundForUser,
    GalleryIsFull,
    APIGalleryIsFull
)
from app.util.mixins import APIErrorsMixin


class FileErrorMixin(APIErrorsMixin):
    @property
    def expected_exceptions(self):
        return {
            **super().expected_exceptions,
            NoGalleryFoundForUser: APINoGalleryFoundForUser,
            GalleryIsFull: APIGalleryIsFull,
        }
