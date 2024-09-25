from django.db import models


class CodexGroups(models.TextChoices):
    DRIFT = "Drift"
    INDEX = "Index"

    @classmethod
    def all(cls) -> list:
        return [cls.DRIFT, cls.INDEX]

    @classmethod
    def reverse(cls) -> list:
        return [cls.INDEX, cls.DRIFT]


class CodexEventTags(models.TextChoices):
    WORKSHOP = "Workshop"
    LECTURE = "Lecture"

    @classmethod
    def all(cls) -> list:
        return [cls.WORKSHOP, cls.LECTURE]
