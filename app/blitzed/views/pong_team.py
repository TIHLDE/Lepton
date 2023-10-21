from app.blitzed.models.pong_team import PongTeam
from app.blitzed.serializers.pong_team import PongTeamSerializer
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet


class PongTeamViewset(BaseViewSet):
    serializer_class = PongTeamSerializer
    permission_classes = [BasicViewPermission]
    queryset = PongTeam.objects.all()
