from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from app.content.models import Event, Strike, User
from app.content.serializers import StrikeSerializer
from app.util.utils import today


class StrikeViewSet(viewsets.ModelViewSet):
    serializer_class = StrikeSerializer
    queryset = Strike.objects.filter(expires_at__gte=today())

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Endepunktet ikke støttet"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )

    def create(self, request):
        request.data["expires_at"] = today() + timedelta(days=20)
        serializer = StrikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(user_id=request.data["user_id"])
            if "event_id" in request.data:
                event = Event.objects.get(id=request.data["event_id"])
                serializer.save(user=user, event=event)
            else:
                serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"detail": "Kunne ikke finne brukeren"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Event.DoesNotExist:
            return Response(
                {"detail": "Kunne ikke finne arrangementet"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"detail": serializer.errors}, status=status.HTTP_409_CONFLICT,)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Prikken ble slettet"}, status=status.HTTP_200_OK,)
