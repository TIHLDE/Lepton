from app.common.serializers import BaseModelSerializer
from app.blitzed.models.beerpong_tournamnet import BeerpongTournament


class BeerpongTournamentSerializer(BaseModelSerializer):
    class Meta:
        model = BeerpongTournament
        fields = ("name", "matches")
        