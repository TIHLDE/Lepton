from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.blitzed.serializers.pong_team import PongTeamSerializer


class PongTeamViewset(BaseViewSet):
    serializer_class = PongTeamSerializer
    permission_classes = [BasicViewPermission]
    