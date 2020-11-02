from enum import Enum

from enumchoicefield import ChoiceEnum


class UserClass(ChoiceEnum):
    FIRST = "1. Klasse"
    SECOND = "2. Klasse"
    THIRD = "3. Klasse"
    FOURTH = "4. Klasse"
    FIFTH = "5. Klasse"


class UserStudy(ChoiceEnum):
    DATAING = "Dataingeniør"
    DIGFOR = "Digital forretningsutvikling"
    DIGINC = "Digital infrastruktur og cybersikkerhet"
    DIGSAM = "Digital samhandling"
    DRIFT = "Drift"


class AdminGroup(ChoiceEnum):
    HS = "HS"
    INDEX = "Index"
    NOK = "Nok"
    PROMO = "Promo"
    SOSIALEN = "Sosialen"


class AppModel(ChoiceEnum):
    EVENT = "Event"
    JOBPOST = "Jobpost"
    NEWS = "News"
    USER = "User"
    CHEATSHEET = "Cheatsheet"


class GroupType(ChoiceEnum):
    THILDE = "THILDE"
    BOARD = "Styre"
    SUBGROUP = "Undergruppe"
    COMMITEE = "Kommite"
    STUDYYEAR = "Studieår"
    OTHER = "Annet"


class EnvironmentOptions(Enum):
    LOCAL = "LOCAL"
    DEVELOPMENT = "DEVELOPMENT"
    PRODUCTION = "PRODUCTION"
