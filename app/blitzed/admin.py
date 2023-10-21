from django.contrib import admin

from app.blitzed.models.session import Session
from app.blitzed.models.pong_team import PongTeam
from app.blitzed.models.pong_match import PongMatch
from app.blitzed.models.pong_result import PongResult
from app.blitzed.models.anonymous_user import AnonymousUser
from app.blitzed.models.beerpong_tournamnet import BeerpongTournament


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    pass

@admin.register(PongTeam)
class PongTeamAdmin(admin.ModelAdmin):
    pass

@admin.register(PongMatch)
class PongMatchAdmin(admin.ModelAdmin):
    pass

@admin.register(PongResult)
class PongResultAdmin(admin.ModelAdmin):
    pass

@admin.register(AnonymousUser)
class AnonymousUserAdmin(admin.ModelAdmin):
    pass

@admin.register(BeerpongTournament)
class BeerpongTournamentAdmin(admin.ModelAdmin):
    pass
