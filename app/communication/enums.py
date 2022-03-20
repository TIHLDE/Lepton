from django.db import models


class UserNotificationSettingType(models.TextChoices):
    REGISTRATION = "REGISTRATION", "Påmelding"
    STRIKE = "STRIKE", "Prikk"
    EVENT_SIGN_OFF_DEADLINE = "EVENT_SIGN_OFF_DEADLINE", "Arrangementer avmeldingsfrist"
    EVENT_EVALUATION = "EVENT_EVALUATION", "Arrangementer evaluering"
    FINE = "FINE", "Gruppebot"
    GROUP_MEMBERSHIP = "GROUP_MEMBERSHIP", "Gruppemedlemsskap"
    OTHER = "OTHER", "Andre"
