from factory.django import DjangoModelFactory

from app.common.enums import UserClass, UserStudy

from ..models import Priority


class PriorityFactory(DjangoModelFactory):
    class Meta:
        model = Priority

    user_class = UserClass.FIRST
    user_study = UserStudy.DATAING
