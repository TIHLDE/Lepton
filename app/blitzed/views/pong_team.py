from rest_framework import status
from rest_framework.response import Response

from app.blitzed.models.pong_team import PongTeam
from app.blitzed.serializers.pong_team import PongTeamSerializer
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet


class PongTeamViewset(BaseViewSet):
    serializer_class = PongTeamSerializer
    permission_classes = [BasicViewPermission]
    queryset = PongTeam.objects.all()

    def destroy(self, request, *args, **kwargs):
        team = self.get_object()
        team.anonymous_members.all().delete()
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Laget ble slettet"}, status=status.HTTP_200_OK)
