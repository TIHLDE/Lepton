import random

from django.db import models
from django.utils.safestring import mark_safe

from app.common.enums import Groups
from app.util.models import BaseModel
from app.content.models.user import User
from app.common.permissions import BasePermissionModel
from app.blitzed.models.anonymous_user import AnonymousUser

class PongTeam(BaseModel, BasePermissionModel):
    team_name = models.CharField(max_length=60, default=generate_team_name)
    members = models.ManyToManyField(User, related_name='pong_teams')
    anonymous_members = models.ManyToManyField(AnonymousUser, blank=True, related_name='pong_teams')

    write_access = [Groups.TIHLDE]

    class Meta:
        verbose_name_plural = 'Pong teams'

    @staticmethod
    def generate_team_name():
        team_names = [
            "Tipsy Titans", 
            "Beer Pong Buddies", 
            "Margarita Mavericks", 
            "Drunken Ducks", 
            "Party Planners",
            ]
        return random.choice(team_names)

    def __str__(self):
        return mark_safe(self.team_name)
