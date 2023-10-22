import random

from django.db import models
from django.utils.safestring import mark_safe

from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel


def generate_tournament_name():
    tournament_names = [
        "Pongapalooza",
        "Beerlympics",
        "Brewski Battle",
        "Fizzed-Up Frenzy",
        "Suds Showdown",
        "Ale-Throw Challenge",
        "Tipsy Trophy Tussle",
        "Mug Madness",
        "IntoxiCup",
        "Cerveza Classic",
    ]
    return random.choice(tournament_names)


class BeerpongTournament(BaseModel, BasePermissionModel):
    name = models.CharField(max_length=60, default=generate_tournament_name)

    class Meta:
        verbose_name_plural = "Pong tournaments"

    def __str__(self):
        return mark_safe(self.name)
