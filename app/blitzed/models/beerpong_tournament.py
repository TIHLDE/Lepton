from django.db import models
from django.utils.safestring import mark_safe

from enumchoicefield import EnumChoiceField

from app.blitzed.enums import TournamentAccess, TournamentStatus
from app.common.permissions import BasePermissionModel
from app.content.models.user import User
from app.util.models import BaseModel


class BeerpongTournament(BaseModel, BasePermissionModel):
    status = EnumChoiceField(TournamentStatus, default=TournamentStatus.PENDING)
    access = EnumChoiceField(TournamentAccess, default=TournamentAccess.PUBLIC)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    pin_code = models.CharField(max_length=4)
    name = models.CharField(max_length=60)

    class Meta:
        verbose_name_plural = "Pong tournaments"

    def __str__(self):
        return mark_safe(self.name)
