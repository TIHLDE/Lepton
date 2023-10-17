from django.db import models
from django.utils.safestring import mark_safe

from app.util.models import BaseModel
from app.blitzed.models.pong_team import PongTeam
from app.blitzed.models.pong_result import PongResult
from app.common.permissions import BasePermissionModel


class PongMatch(BaseModel, BasePermissionModel):
    team1 = models.ForeignKey(PongTeam, on_delete=models.CASCADE, related_name='matches_team1')
    team2 = models.ForeignKey(PongTeam, on_delete=models.CASCADE, related_name='matches_team2')
    result = models.ForeignKey(PongResult, on_delete=models.CASCADE, null=True, blank=True)
    prev_match = models.OneToOneField('self', on_delete=models.SET_NULL, null=True, blank=True)


    class Meta:
        verbose_name_plural = 'Matches'

    def __str__(self):
        return mark_safe(f"{self.team1} vs. {self.team2}")
