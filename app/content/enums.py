from django.db import models


class JobPostType(models.TextChoices):
    PART_TIME = "PART_TIME", "Deltid"
    FULL_TIME = "FULL_TIME", "Fulltid"
    SUMMER_JOB = "SUMMER_JOB", "Sommerjobb"
    OTHER = "OTHER", "Andre"


class UserClass(models.IntegerChoices):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FORTH = 4
    FIFTH = 5
