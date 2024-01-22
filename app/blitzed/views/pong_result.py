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
            self._update_match_tree(instance.match)
            return Response(
                {"detail": "Resultat ble slettet"}, status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"detail": "Noe gikk galt ved sletting av resultat."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def _update_match_tree(self, match):
        if match.future_match is None:
            return

        team1 = match.team1
        team2 = match.team2
        stack = [match.future_match]
        while stack:
            current_match = stack.pop()
            if current_match is None:
                continue
            if not self._team_in_match(current_match, team1, team2):
                continue

            if current_match.team1 in {team1, team2}:
                current_match.team1 = None
            else:
                current_match.team2 = None

            if PongResult.objects.filter(match=current_match.id).exists():
                PongResult.objects.get(match=current_match.id).delete()

            current_match.save()
            stack.append(current_match.future_match)

    def _team_in_match(self, match, team1, team2):
        return team1 in {match.team1, match.team2} or team2 in {
            match.team1,
            match.team2,
        }
