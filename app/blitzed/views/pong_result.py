from rest_framework import status
from rest_framework.response import Response

from app.blitzed.models.pong_match import PongMatch
from app.blitzed.models.pong_result import PongResult
from app.blitzed.serializers.pong_result import (
    PongResultCreateAndUpdateSerializer,
    PongResultSerializer,
)
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet


class PongResultViewset(BaseViewSet):
    serializer_class = PongResultSerializer
    permission_classes = [BasicViewPermission]
    queryset = PongResult.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            serializer = PongResultCreateAndUpdateSerializer(
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
                {"detail": "Noe gikk galt ved lagring av resultat"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            result = self.get_object()
            serializer = PongResultCreateAndUpdateSerializer(
                result, data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                result = super().perform_update(serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(
                {"detail": "Klarte ikke oppdatere resultat"},
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
            self.update_match_tree(instance.match.id)
            return Response(
                {"detail": "Resultat ble slettet"}, status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"detail": "Noe gikk galt ved sletting av resultat"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update_match_tree(self, match_id):
        current_match = PongMatch.objects.get(id=match_id)
        if current_match.future_match is None:
            return

        next_match = current_match.future_match
        if current_match.team1 == next_match.team1:
            next_match.team1 = None
        elif current_match.team2 == next_match.team1:
            next_match.team1 = None
        else:
            next_match.team2 = None
        self.update_match_tree(next_match.id)
        next_match.save()
