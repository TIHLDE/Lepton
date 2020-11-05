import uuid

import factory
from factory.django import DjangoModelFactory

from app.common.enums import CheatsheetType, UserClass, UserStudy
from app.content.models import Cheatsheet


class CheatsheetFactory(DjangoModelFactory):
    """Factory that creates a generic cheatsheet"""

    class Meta:
        model = Cheatsheet

    id = uuid.uuid4()
    title = factory.Sequence(lambda n: f"Cheatsheet{n}")
    creator = factory.Faker("name")
    study = factory.Iterator(UserStudy)
    grade = factory.Iterator(UserClass)
    course = factory.Faker("word")
    type = factory.Iterator(CheatsheetType)
    official = False
    url = factory.LazyAttributeSequence(lambda o, n: f"http://www.{o.title}example.com")
