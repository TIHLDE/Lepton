from django.db.models import Q
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.response import Response

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.kontres.models.reservation import Reservation
from app.kontres.serializer.reservation_seralizer import ReservationSerializer


class ReservationViewSet(BaseViewSet):
    permission_classes = [BasicViewPermission]
    serializer_class = ReservationSerializer

    def get_queryset(self):
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        # Convert string dates to datetime objects
        if start_date:
            start_date = parse_datetime(start_date)
        if end_date:
            end_date = parse_datetime(end_date)

        # Adjusted filter to capture overlapping reservations
        if start_date and end_date:
            queryset = Reservation.objects.filter(
                Q(start_time__lt=end_date) & Q(end_time__gt=start_date)
            )
            return queryset

        return Reservation.objects.all()

    def create(self, request, *args, **kwargs):
        request.data["author"] = request.user.user_id
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            # Overriding the state to PENDING
            serializer.validated_data["state"] = "PENDING"
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        reservation = self.get_object()
        serializer = self.get_serializer(reservation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        reservation = self.get_object()

        if not reservation.has_object_destroy_permission(request):
            return Response({"melding": "Du har ikke tilgang til å slette denne reservasjonen."},
                            status=status.HTTP_403_FORBIDDEN)

        reservation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
