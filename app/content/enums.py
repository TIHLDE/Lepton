from django.db import models

from enumchoicefield import ChoiceEnum


class UserClass(models.IntegerChoices):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FORTH = 4
    FIFTH = 5

class ContentType(models.TextChoices):
    EVENT = "event"
    NEWS = "news"

class CategoryEnum(ChoiceEnum):
    ACTIVITY = "Aktivitet"
    SOSIALT = "Sosialt"
    BEDPRES = "Bedpres"
    KURS = "Kurs"
    ANNET = "Annet"
    FADDERUKA = "Fadderuka"
