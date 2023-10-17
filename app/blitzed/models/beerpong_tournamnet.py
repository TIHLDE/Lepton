import random

from django.db import models
from django.utils.safestring import mark_safe

from app.util.models import BaseModel
from app.blitzed.models.pong_match import PongMatch
from app.common.permissions import BasePermissionModel


class BeerpongTournament(BaseModel, BasePermissionModel):
    name = models.CharField(max_length=60, default=generate_tournament_name)
    matches = models.ManyToManyField(PongMatch, related_name='tournaments')

    class Meta:
        verbose_name_plural = 'Pong tournaments'

    @staticmethod
    def generate_tournament_name():
        team_names = [
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
        return random.choice(team_names)

    def __str__(self):
        return mark_safe(self.name)
