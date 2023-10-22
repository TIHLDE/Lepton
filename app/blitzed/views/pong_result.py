from app.blitzed.models.pong_result import PongResult
from app.blitzed.serializers.pong_result import PongResultSerializer
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet


class PongResultViewset(BaseViewSet):
    serializer_class = PongResultSerializer
    permission_classes = [BasicViewPermission]
    queryset = PongResult.objects.all()
