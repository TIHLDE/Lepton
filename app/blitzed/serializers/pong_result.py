from app.blitzed.models.pong_result import PongResult
from app.common.serializers import BaseModelSerializer


class PongResultSerializer(BaseModelSerializer):
    class Meta:
        model = PongResult
        fields = ("winner", "result")
