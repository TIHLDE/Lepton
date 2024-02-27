from enumchoicefield import ChoiceEnum


class EventFormType(ChoiceEnum):
    SURVEY = "Survey"
    EVALUATION = "Evaluation"


class FormFieldType(ChoiceEnum):
    TEXT_ANSWER = "Text answer"
    MULTIPLE_SELECT = "Multiple select"
    SINGLE_SELECT = "Single select"
    TEXT_DESCRIPTION = "Text description"
