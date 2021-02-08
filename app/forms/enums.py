from django.utils.translation import gettext_lazy as _
from enumchoicefield import ChoiceEnum


class EventFormType(ChoiceEnum):
    SURVEY = _("Survey")
    EVALUATION = _("Evaluation")


class FormFieldType(ChoiceEnum):
    TEXT_ANSWER = _("Text answer")
    MULTIPLE_SELECT = _("Multiple select")
    SINGLE_SELECT = _("Single select")
