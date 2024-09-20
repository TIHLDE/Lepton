from enumchoicefield import ChoiceEnum
from django.db import models


# This must be here because of the migrations files
class EventFormType(ChoiceEnum):
    SURVEY = "Survey"
    EVALUATION = "Evaluation"


class NativeEventFormType(models.TextChoices):
    SURVEY = "SURVEY", "Survey"
    EVALUATION = "EVALUATION", "Evaluation"


# This must be here because of the migrations files
class FormFieldType(ChoiceEnum):
    TEXT_ANSWER = "Text answer"
    MULTIPLE_SELECT = "Multiple select"
    SINGLE_SELECT = "Single select"


class NativeFormFieldType(models.TextChoices):
    TEXT_ANSWER = "TEXT_ANSWER", "Text answer"
    MULTIPLE_SELECT = "MULTIPLE_SELECT", "Multiple select"
    SINGLE_SELECT = "SINGLE_SELECT", "Single select"
