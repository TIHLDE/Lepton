from django.db import models


class UserNotificationSettingType(models.TextChoices):
    REGISTRATION = "REGISTRATION", "Påmeldingsoppdateringer"
    UNREGISTRATION = "UNREGISTRATION", "Avmeldingsoppdateringer"
    STRIKE = "STRIKE", "Prikkoppdateringer"
    EVENT_SIGN_UP_START = "EVENT_SIGN_UP_START", "Arrangementer - påmeldingsstart"
    EVENT_SIGN_OFF_DEADLINE = (
        "EVENT_SIGN_OFF_DEADLINE",
        "Arrangementer - avmeldingsfrist",
    )
    EVENT_EVALUATION = "EVENT_EVALUATION", "Arrangementer - evaluering"
    EVENT_INFO = "EVENT_INFO", "Arrangementer - info fra arrangør"
    FINE = "FINE", "Grupper - bot"
    GROUP_MEMBERSHIP = "GROUP_MEMBERSHIP", "Grupper - medlemsskap"
    OTHER = "OTHER", "Andre"
    RESERVATION_NEW = "RESERVATION NEW", "Ny reservasjon"
    RESERVATION_APPROVED = "RESERVATION APPROVED", "Godkjent reservasjon"
    RESERVATION_CANCELLED = "RESERVATION CANCELLED", "Avslått reservasjon"
    KONTRES = "KONTRES", "Kontres"
    BLITZED = "BLITZED", "Blitzed"
    UTLEGG = "UTLEGG", "Utlegg"

    @classmethod
    def get_kontres_and_blitzed(cls):
        return [cls.KONTRES, cls.BLITZED]
