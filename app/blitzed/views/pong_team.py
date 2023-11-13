from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.blitzed.models.pong_team import PongTeam
from app.blitzed.serializers.pong_team import (
    PongTeamCreateAndUpdateSerializer,
    PongTeamSerializer,
)
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet


class PongTeamViewset(BaseViewSet):
    serializer_class = PongTeamSerializer
    permission_classes = [BasicViewPermission]
    queryset = PongTeam.objects.all()

    def get_serializer_class(self):
        if self.action == "create" or self.action == "update":
            return PongTeamCreateAndUpdateSerializer
        return self.serializer_class

    @action(detail=False, methods=["GET"])
    def get_team_by_tournament_id(self, request, *args, **kwargs):
        tournament_id = request.query_params.get("tournament")
        teams = PongTeam.objects.filter(tournament=tournament_id)
        if teams.count() == 0:
            return Response({"detail": "Fant ingen lag tilhørende turnering"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PongTeamSerializer(teams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        try:
            serializer = PongTeamCreateAndUpdateSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                super().perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(
                {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {"detail": "Noe gikk galt ved lagring av lag."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            serializer = PongTeamCreateAndUpdateSerializer(
                data=request.data, partial=True, context={"request": request}
            )
            if serializer.is_valid():
                super().update(serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(
                {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {"detail": "Noe gikk galt ved oppdatering."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        team = self.get_object()
        team.anonymous_members.all().delete()
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Laget ble slettet"}, status=status.HTTP_200_OK)
