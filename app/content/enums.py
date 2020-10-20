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
