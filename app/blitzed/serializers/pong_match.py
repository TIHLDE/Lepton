from rest_framework import serializers

from app.blitzed.models.pong_match import PongMatch
from app.blitzed.serializers.pong_result import PongResultSerializer
from app.blitzed.serializers.pong_team import SimplePongTeamSerializer
from app.common.serializers import BaseModelSerializer


class PongMatchSerializer(BaseModelSerializer):
    result = PongResultSerializer(required=False)
    team1 = SimplePongTeamSerializer()
    team2 = SimplePongTeamSerializer()

    class Meta:
        model = PongMatch
        fields = ("id", "team1", "team2", "result", "future_match")


class SimplePongMatchSerializer(BaseModelSerializer):
    team1 = SimplePongTeamSerializer()
    team2 = SimplePongTeamSerializer()

    class Meta:
        model = PongMatch
        fields = ("id", "team1", "team2", "future_match")


class PongMatchCreateAndUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PongMatch
        fields = ("id", "team1", "team2", "future_match", "tournament")
