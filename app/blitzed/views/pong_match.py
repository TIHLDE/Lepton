from rest_framework import status
from rest_framework.response import Response

from app.blitzed.models.pong_match import PongMatch
from app.blitzed.serializers.pong_match import (
    PongMatchCreateAndUpdateSerializer,
    PongMatchSerializer,
)
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet


class PongMatchViewset(BaseViewSet):
    serializer_class = PongMatchSerializer
    permission_classes = [BasicViewPermission]
    queryset = PongMatch.objects.all()

    def get_serializer_class(self):
        if self.action == "create" or self.action == "update":
            return PongMatchCreateAndUpdateSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        try:
            serializer = PongMatchCreateAndUpdateSerializer(
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
                {"detail": "Noe gikk galt ved lagring av kamp."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        try:
            match = self.get_object()
            serializer = PongMatchCreateAndUpdateSerializer(
                match, data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                super().update(serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {"detail": "Noe gikk galt ved oppdatering av kamp."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Kampen ble slettet"}, status=status.HTTP_200_OK)
