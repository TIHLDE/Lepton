from django.db import models


class UserClass(models.IntegerChoices):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FORTH = 4
    FIFTH = 5


class CategoryEnum(models.TextChoices):
    ACTIVITY = "Aktivitet"
    SOSIALT = "Sosialt"
    BEDPRES = "Bedpres"
    KURS = "Kurs"
    ANNET = "Annet"
    FADDERUKA = "Fadderuka"


class MinuteTagEnum(models.TextChoices):
    MINUTE = "Møtereferat"
    DOCUMENT = "Dokument"
