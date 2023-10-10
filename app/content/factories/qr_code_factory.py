import factory
from factory.django import DjangoModelFactory

from app.content.models import QRCode
from app.content.factories.user_factory import UserFactory


class QRCodeFactory(DjangoModelFactory):
    class Meta:
        model = QRCode

    name = factory.Sequence(lambda n: f"QRCode {n}")
    user = factory.SubFactory(UserFactory)
    image = "https://tihldestorage.blob.core.windows.net/imagepng/0331423a-11b3-4e6b-a505-f84e0991b696TestCode"