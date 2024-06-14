from django.db import models
from django.utils.safestring import mark_safe

from app.blitzed.models.anonymous_user import AnonymousUser
from app.blitzed.models.beerpong_tournament import BeerpongTournament
from app.common.permissions import BasePermissionModel
from app.content.models.user import User
from app.util.models import BaseModel


class PongTeam(BaseModel, BasePermissionModel):
    team_name = models.CharField(max_length=60)
    members = models.ManyToManyField(User, blank=True, related_name="pong_teams")
    anonymous_members = models.ManyToManyField(
        AnonymousUser, blank=True, related_name="pong_teams"
    )
    tournament = models.ForeignKey(
        BeerpongTournament, on_delete=models.CASCADE, related_name="teams"
    )
    icon_id = models.CharField(max_length=60, blank=True, null=True)

    class Meta:
        verbose_name = "Pong team"
        verbose_name_plural = "Pong teams"

    def __str__(self):
        return mark_safe(self.team_name)
