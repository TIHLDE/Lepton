import factory
from factory.django import DjangoModelFactory

from app.content.factories.user_factory import UserFactory
from app.content.models import QRCode


class QRCodeFactory(DjangoModelFactory):
    class Meta:
        model = QRCode

    name = factory.Sequence(lambda n: f"QRCode {n}")
    user = factory.SubFactory(UserFactory)
    content = "https://tihlde.org"
