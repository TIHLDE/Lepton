from rest_framework import serializers

from app.blitzed.models.pong_match import PongMatch
from app.blitzed.serializers.pong_result import PongResultSerializer
from app.common.serializers import BaseModelSerializer


class PongMatchSerializer(BaseModelSerializer):
    result = PongResultSerializer(required=False)

    class Meta:
        model = PongMatch
        fields = ("team1", "team2", "result", "prev_match")


class PongMatchCreateAndUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PongMatch
        fields = ("team1", "team2", "prev_match", "tournament")
