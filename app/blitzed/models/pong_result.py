from django.db import models
from django.utils.safestring import mark_safe

from app.blitzed.models.pong_match import PongMatch
from app.blitzed.models.pong_team import PongTeam
from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel


class PongResult(BaseModel, BasePermissionModel):
    id = models.AutoField(primary_key=True)
    match = models.OneToOneField(
        PongMatch, on_delete=models.CASCADE, related_name="result"
    )
    winner = models.ForeignKey(
        PongTeam,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="match_winners",
    )
    result = models.CharField(max_length=10, default="0 - 0")

    class Meta:
        verbose_name_plural = "Match results"

    def __str__(self):
        return mark_safe(f"Winner:{self.winner} -> {self.result}")
