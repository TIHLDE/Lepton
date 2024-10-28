from app.files.exceptions import FileDoesNotExist, FileDoesNotExistException
from app.util.mixins import APIErrorsMixin


class FileErrorMixin(APIErrorsMixin):
    @property
    def expected_exceptions(self):
        return {
            **super().expected_exceptions,
            FileDoesNotExist: FileDoesNotExistException,
        }
