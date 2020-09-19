from factory.django import DjangoModelFactory

from ..models import Priority
from ..enums import UserClass, UserStudy


class PriorityFactory(DjangoModelFactory):

    class Meta:
        model = Priority

    user_class = UserClass.FIRST
    user_study = UserStudy.DATAING


