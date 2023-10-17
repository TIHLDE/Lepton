from app.common.serializers import BaseModelSerializer
from app.blitzed.models.pong_result import PongResult


class PongResultSerializer(BaseModelSerializer):
    class Meta:
        model = PongResult
        fields = ("match", "winner", "result")
        