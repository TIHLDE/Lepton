from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from app.content.models import (
    Event,
    Strike,
    User,
    get_strike_description,
    get_strike_strike_size,
)
from app.content.serializers import StrikeSerializer


class StrikeViewSet(viewsets.ModelViewSet):
    serializer_class = StrikeSerializer
    queryset = Strike.objects.all()

    def get_queryset(self):
        return (strike for strike in Strike.objects.all() if strike.active)

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Endepunktet ikke støttet"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )

    def create(self, request):
        if "enum" in request.data:
            enum = request.data["enum"]
            request.data["description"] = get_strike_description(enum)
            request.data["strike_size"] = get_strike_strike_size(enum)
        serializer = StrikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, user_id=request.data["user_id"])
        if "event_id" in request.data:
            event = get_object_or_404(Event, id=request.data["event_id"])
            serializer.save(user=user, event=event)
        else:
            serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Prikken ble slettet"}, status=status.HTTP_200_OK)
