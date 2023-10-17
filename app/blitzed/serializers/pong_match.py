from app.common.serializers import BaseModelSerializer
from app.blitzed.models.pong_match import PongMatch


class PongMatchSerializer(BaseModelSerializer):
    class Meta:
        model = PongMatch
        fields = ("team1", "team2", "result", "prev_match")
        