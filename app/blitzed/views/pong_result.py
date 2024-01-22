from rest_framework import status
from rest_framework.response import Response

from app.blitzed.models.pong_result import PongResult
from app.blitzed.serializers.pong_result import (
    PongResultCreateSerializer,
    PongResultSerializer,
    PongResultUpdateSerializer,
)
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet


class PongResultViewset(BaseViewSet):
    serializer_class = PongResultSerializer
    permission_classes = [BasicViewPermission]
    queryset = PongResult.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            serializer = PongResultCreateSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                super().perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(
                {"detail": "Klarte ikke lagre resultat"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"detail": "Noe gikk galt ved lagring av resultat."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            result = self.get_object()
            serializer = PongResultUpdateSerializer(
                result, data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                result = super().perform_update(serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(
                {"detail": "Klarte ikke oppdatere resultat."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {"detail": "Noe gikk galt ved oppdatering av resultat"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            super().destroy(request, *args, **kwargs)
            self.update_match_tree(
                instance.match, instance.match.team1, instance.match.team2
            )
            return Response(
                {"detail": "Resultat ble slettet"}, status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"detail": "Noe gikk galt ved sletting av resultat."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update_match_tree(self, current_match, team1, team2):
        if current_match.future_match is None:
            return

        next_match = current_match.future_match
        if not self.team_in_match(next_match, team1, team2):
            return

        if next_match.team1 in {team1, team2}:
            next_match.team1 = None
        else:
            next_match.team2 = None

        self.update_match_tree(next_match, team1, team2)
        if PongResult.objects.filter(match=next_match.id).exists():
            PongResult.objects.get(match=next_match.id).delete()
        next_match.save()

    def team_in_match(self, match, team1, team2):
        return team1 in {match.team1, match.team2} or team2 in {
            match.team1,
            match.team2,
        }
