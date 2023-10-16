from django.db import models
from django.utils.safestring import mark_safe

from app.common.enums import Groups
from app.util.models import BaseModel
from app.blitzed.models.pong_team import PongTeam
from app.common.permissions import BasePermissionModel


class PongResult(BaseModel, BasePermissionModel):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='match_results')
    winner = models.ForeignKey(PongTeam, on_delete=models.CASCADE, null=True, blank=True, related_name='match_winners')
    result = models.CharField(max_length=10, default='0 - 0')

    write_access = [Groups.TIHLDE]

    class Meta:
        verbose_name_plural = 'Matche results'

    def __str__(self):
        return mark_safe(f"Winner:{self.winner} -> {self.result}")
