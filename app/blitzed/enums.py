from enumchoicefield import ChoiceEnum


class TournamentStatus(ChoiceEnum):
    PENDING = ("PENDING",)
    ACTIVE = ("ACTIVE",)
    FINISHED = ("FINISHED",)


class TournamentAccess(ChoiceEnum):
    PUBLIC = ("PUBLIC",)
    PIN = ("PIN",)
