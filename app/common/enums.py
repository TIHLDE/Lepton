from enum import Enum

from django.db import models

from enumchoicefield import ChoiceEnum


class UserClass(ChoiceEnum):
    FIRST = "1. Klasse"
    SECOND = "2. Klasse"
    THIRD = "3. Klasse"
    FOURTH = "4. Klasse"
    FIFTH = "5. Klasse"
    ALUMNI = "Alumni"


class UserStudy(ChoiceEnum):
    DATAING = "Dataingeniør"
    DIGFOR = "Digital forretningsutvikling"
    DIGINC = "Digital infrastruktur og cybersikkerhet"
    DIGSAM = "Digital samhandling"
    DRIFT = "Drift"
    INFO = "Informasjonsbehandling"


class AdminGroup(ChoiceEnum):
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


class Groups(ChoiceEnum):
    TIHLDE = "TIHLDE"
    JUBKOM = "JubKom"
    REDAKSJONEN = "Redaksjonen"
    FONDET = "Forvaltningsgruppen"
    PLASK = "Plask"
    DRIFT = "Drift"


class AppModel(ChoiceEnum):
    EVENT = "Event"
    JOBPOST = "Jobpost"
    NEWS = "News"
    USER = "User"
    CHEATSHEET = "Cheatsheet"
    WEEKLY_BUSINESS = "Weekly Business"


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

    @classmethod
    def all(cls):
        return list(map(lambda c: (c.name, c.value), cls))


class EnvironmentOptions(Enum):
    LOCAL = "LOCAL"
    DEVELOPMENT = "DEVELOPMENT"
    PRODUCTION = "PRODUCTION"


class CheatsheetType(ChoiceEnum):
    FILE = "Fil"
    GITHUB = "GitHub"
    LINK = "Link"
    OTHER = "Annet"


class MembershipType(ChoiceEnum):
    LEADER = "Leader"
    MEMBER = "Member"

    @classmethod
    def board_members(cls):
        return (cls.LEADER,)

    @classmethod
    def all(cls):
        return tuple((i.name, i.value) for i in cls)


class StrikeEnum(ChoiceEnum):
    PAST_DEADLINE = "PAST_DEADLINE"
    NO_SHOW = "NO_SHOW"
    LATE = "LATE"
    BAD_BEHAVIOR = "BAD_BEHAVIOR"
    EVAL_FORM = "EVAL_FORM"


class CodexGroups(models.TextChoices):
    DRIFT = "Drift"
    INDEX = "Index"

    @classmethod
    def all(cls) -> list:
        return [cls.DRIFT, cls.INDEX]

    @classmethod
    def reverse(cls) -> list:
        return [cls.INDEX, cls.DRIFT]
