from enum import Enum

from django.db import models

from enumchoicefield import ChoiceEnum


# This can't be removed because it is used in the migrations. It is not used in the code.
class UserClass(ChoiceEnum):
    FIRST = "1. Klasse"
    SECOND = "2. Klasse"
    THIRD = "3. Klasse"
    FOURTH = "4. Klasse"
    FIFTH = "5. Klasse"
    ALUMNI = "Alumni"


class NativeUserClass(models.TextChoices):
    FIRST = "FIRST", "1. Klasse"
    SECOND = "SECOND", "2. Klasse"
    THIRD = "THIRD", "3. Klasse"
    FOURTH = "FOURTH", "4. Klasse"
    FIFTH = "FIFTH", "5. Klasse"
    ALUMNI = "ALUMNI", "Alumni"


def get_user_class_number(user_class: NativeUserClass) -> int:
    _class = user_class.label
    if user_class == NativeUserClass.ALUMNI:
        return 6
    return int(_class.split(".")[0])


# This can't be removed because it is used in the migrations. It is not used in the code
class UserStudy(ChoiceEnum):
    DATAING = "Dataingeniør"
    DIGFOR = "Digital forretningsutvikling"
    DIGINC = "Digital infrastruktur og cybersikkerhet"
    DIGSAM = "Digital samhandling"
    DRIFT = "Drift"
    INFO = "Informasjonsbehandling"


class NativeUserStudy(models.TextChoices):
    DATAING = "DATAING", "Dataingeniør"
    DIGFOR = "DIGFOR", "Digital forretningsutvikling"
    DIGINC = "DIGINC", "Digital infrastruktur og cybersikkerhet"
    DIGSAM = "DIGSAM", "Digital samhandling"
    DRIFT = "DRIFT", "Drift"
    INFO = "INFO", "Informasjonsbehandling"


class AdminGroup(models.TextChoices):
    HS = "HS"
    INDEX = "Index"
    NOK = "Nok"
    PROMO = "Promo"
    SOSIALEN = "Sosialen"
    KOK = "Kontkom"

    @classmethod
    def all(cls):
        return (cls.HS, cls.INDEX, cls.NOK, cls.PROMO, cls.SOSIALEN, cls.KOK)

    @classmethod
    def admin(cls):
        return (cls.HS, cls.INDEX)


class Groups(models.TextChoices):
    TIHLDE = "TIHLDE"
    JUBKOM = "JubKom"
    REDAKSJONEN = "Redaksjonen"
    FONDET = "Forvaltningsgruppen"
    PLASK = "Plask"
    DRIFT = "Drift"

    @classmethod
    def all(cls):
        return (cls.TIHLDE, cls.JUBKOM, cls.REDAKSJONEN, cls.FONDET, cls.PLASK, cls.DRIFT)


# This can't be removed because it is used in the migrations. It is not used in the code.
class GroupType(ChoiceEnum):
    TIHLDE = "TIHLDE"
    BOARD = "Styre"
    SUBGROUP = "Undergruppe"
    COMMITTEE = "Komité"
    STUDYYEAR = "Studieår"
    STUDY = "Studie"
    INTERESTGROUP = "Interesse Gruppe"
    OTHER = "Annet"

    @classmethod
    def public_groups(cls):
        return [cls.BOARD, cls.SUBGROUP, cls.COMMITTEE, cls.INTERESTGROUP]


class NativeGroupType(models.TextChoices):
    TIHLDE = "TIHLDE", "TIHLDE"
    BOARD = "BOARD", "Styre"
    SUBGROUP = "SUBGROUP", "Undergruppe"
    COMMITTEE = "COMMITTEE", "Komité"
    STUDYYEAR = "STUDYYEAR", "Studieår"
    STUDY = "STUDY", "Studie"
    INTERESTGROUP = "INTERESTGROUP", "Interesse Gruppe"
    OTHER = "OTHER", "Annet"

    @classmethod
    def public_groups(cls):
        return [cls.BOARD, cls.SUBGROUP, cls.COMMITTEE, cls.INTERESTGROUP]


class EnvironmentOptions(Enum):
    LOCAL = "LOCAL"
    DEVELOPMENT = "DEVELOPMENT"
    PRODUCTION = "PRODUCTION"


# This can't be removed because it is used in the migrations. It is not used in the code
class CheatsheetType(ChoiceEnum):
    FILE = "Fil"
    GITHUB = "GitHub"
    LINK = "Link"
    OTHER = "Annet"


class NativeCheatsheetType(models.TextChoices):
    FILE = "FILE", "Fil"
    GITHUB = "GITHUB", "GitHub"
    LINK = "LINK", "Link"
    OTHER = "OTHER", "Annet"


# This can't be removed because it is used in the migrations. It is not used in the code
class MembershipType(ChoiceEnum):
    LEADER = "Leader"
    MEMBER = "Member"

    @classmethod
    def board_members(cls):
        return (cls.LEADER,)

    @classmethod
    def all(cls):
        return tuple((i.name, i.value) for i in cls)


class NativeMembershipType(models.TextChoices):
    LEADER = "LEADER", "Leader"
    MEMBER = "MEMBER", "Member"

    @classmethod
    def board_members(cls):
        return (cls.LEADER,)


# This can't be removed because it is used in the migrations. It is not used in the code
class StrikeEnum(ChoiceEnum):
    PAST_DEADLINE = "PAST_DEADLINE"
    NO_SHOW = "NO_SHOW"
    LATE = "LATE"
    BAD_BEHAVIOR = "BAD_BEHAVIOR"
    EVAL_FORM = "EVAL_FORM"


class NativeStrikeEnum(models.TextChoices):
    PAST_DEADLINE = "PAST_DEADLINE"
    NO_SHOW = "NO_SHOW"
    LATE = "LATE"
    BAD_BEHAVIOR = "BAD_BEHAVIOR"
    EVAL_FORM = "EVAL_FORM"

    @classmethod
    def all(cls):
        return [cls.PAST_DEADLINE, cls.NO_SHOW, cls.LATE, cls.BAD_BEHAVIOR, cls.EVAL_FORM]


class CodexGroups(models.TextChoices):
    DRIFT = "Drift"
    INDEX = "Index"

    @classmethod
    def all(cls) -> list:
        return [cls.DRIFT, cls.INDEX]

    @classmethod
    def reverse(cls) -> list:
        return [cls.INDEX, cls.DRIFT]
