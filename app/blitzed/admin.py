from django.contrib import admin

from app.blitzed.models.anonymous_user import AnonymousUser
from app.blitzed.models.beerpong_tournament import BeerpongTournament
from app.blitzed.models.pong_match import PongMatch
from app.blitzed.models.pong_result import PongResult
from app.blitzed.models.pong_team import PongTeam
from app.blitzed.models.session import Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    pass


@admin.register(PongTeam)
class PongTeamAdmin(admin.ModelAdmin):
    search_fields = [
        "team_name",
        "members__first_name",
        "members__last_name",
        "anonymous_members__name",
        "tournament__name",
    ]


@admin.register(PongMatch)
class PongMatchAdmin(admin.ModelAdmin):
    search_fields = [
        "team1__team_name",
        "team2__team_name",
        "tournament__name",
    ]


@admin.register(PongResult)
class PongResultAdmin(admin.ModelAdmin):
    search_fields = [
        "match__team1__team_name",
        "match__team2__team_name",
        "match__tournament__name",
    ]


@admin.register(AnonymousUser)
class AnonymousUserAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(BeerpongTournament)
class BeerpongTournamentAdmin(admin.ModelAdmin):
    search_fields = ["name"]
