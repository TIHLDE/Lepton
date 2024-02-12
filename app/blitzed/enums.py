from enumchoicefield import ChoiceEnum


class TournamentStatus(ChoiceEnum):
    PENDING = ("PENDING",)
    ACTIVE = ("ACTIVE",)
    FINISHED = ("FINISHED",)


class TournamentAccess(ChoiceEnum):
    USER_ONLY = ("USER_ONLY",)
    PUBLIC = ("PUBLIC",)
    PIN = ("PIN",)
