from enumchoicefield import ChoiceEnum


class FormType(ChoiceEnum):
    GENERAL = "Generelt"
    SURVEY = "Undersøkelse"
    EVALUATION = "Evaluering"


class FormFieldType(ChoiceEnum):
    TEXT_ANSWER = 'Text answer'
    MULTIPLE_SELECT = 'Multiple select'
    SINGLE_SELECT = 'Single select'
