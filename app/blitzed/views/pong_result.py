from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.blitzed.serializers.pong_result import PongResultSerializer


class PongResultViewset(BaseViewSet):
    serializer_class = PongResultSerializer
    permission_classes = [BasicViewPermission]
    