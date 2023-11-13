from django.db import models
from django.utils.safestring import mark_safe

from app.blitzed.models.beerpong_tournament import BeerpongTournament
from app.blitzed.models.pong_team import PongTeam
from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel


class PongMatch(BaseModel, BasePermissionModel):
    team1 = models.ForeignKey(
        PongTeam, on_delete=models.SET_NULL, related_name="matches_team1", null=True
    )
    team2 = models.ForeignKey(
        PongTeam, on_delete=models.SET_NULL, related_name="matches_team2", null=True
    )
    future_match = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    tournament = models.ForeignKey(
        BeerpongTournament, on_delete=models.CASCADE, related_name="matches"
    )

    class Meta:
        verbose_name_plural = "Matches"

    def __str__(self):
        return mark_safe(f"{self.team1} vs. {self.team2}")
