from app.blitzed.serializers.pong_match import PongMatchSerializer
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet


class PongMatchViewset(BaseViewSet):
    serializer_class = PongMatchSerializer
    permission_classes = [BasicViewPermission]
