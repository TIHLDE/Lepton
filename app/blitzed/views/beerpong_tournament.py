from rest_framework import status
from rest_framework.response import Response

from app.blitzed.models.beerpong_tournament import BeerpongTournament
from app.blitzed.serializers.beerpong_tournament import (
    BeerpongTournamentSerializer,
)
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet


class BeerpongTournamentViewset(BaseViewSet):
    serializer_class = BeerpongTournamentSerializer
    permission_classes = [BasicViewPermission]
    queryset = BeerpongTournament.objects.all()

    def destroy(self, request, *args, **kwargs):
        tournament = self.get_object()
        tournament.teams.all().delete()
        tournament.matches.all().delete()
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Turnering ble slettet"}, status=status.HTTP_200_OK)
