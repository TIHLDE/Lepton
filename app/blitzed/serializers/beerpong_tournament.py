from app.blitzed.models.beerpong_tournament import BeerpongTournament
from app.blitzed.serializers.pong_match import PongMatchSerializer
from app.blitzed.serializers.pong_team import SimplePongTeamSerializer
from app.common.serializers import BaseModelSerializer


class BeerpongTournamentSerializer(BaseModelSerializer):
    matches = PongMatchSerializer(required=False, many=True)
    teams = SimplePongTeamSerializer(required=False, many=True)

    class Meta:
        model = BeerpongTournament
        fields = ("id", "name", "matches", "teams")


class BeerpongTournamentGeneratedSerializer(BaseModelSerializer):
    matches = PongMatchSerializer(required=False, many=True)

    class Meta:
        model = BeerpongTournament
        fields = ("id", "matches")
