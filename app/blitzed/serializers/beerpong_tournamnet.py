from app.blitzed.models.beerpong_tournamnet import BeerpongTournament
from app.common.serializers import BaseModelSerializer


class BeerpongTournamentSerializer(BaseModelSerializer):
    class Meta:
        model = BeerpongTournament
        fields = ("name", "matches")
