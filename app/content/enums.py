from django.db import models

from enumchoicefield import ChoiceEnum


class UserClass(models.IntegerChoices):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FORTH = 4
    FIFTH = 5


class CategoryEnum(ChoiceEnum):
    ACTIVITY = "Aktivitet"
    SOSIALT = "Sosialt"
    BEDPRES = "Bedpres"
    KURS = "Kurs"
    ANNET = "Annet"
    FADDERUKA = "Fadderuka"


class MinuteTagEnum(models.TextChoices):
    MINUTE = "Møtereferat"
    DOCUMENT = "Dokument"
