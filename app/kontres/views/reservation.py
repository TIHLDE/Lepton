from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from app.common.permissions import is_admin_user
from app.kontres.models.reservation import Reservation
from app.kontres.serializer.reservation_seralizer import ReservationSerializer


class ReservationViewSet(viewsets.ViewSet):
    def get_queryset(self):
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        if start_date == "0" and end_date == "0":
            return Reservation.objects.all()
        elif start_date and end_date:
            return Reservation.objects.filter(
                start_time__gte=start_date, end_time__lte=end_date
            )
        else:
            return Reservation.objects.all()

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        reservation = get_object_or_404(queryset, pk=pk)
        serializer = ReservationSerializer(reservation)
        return Response(serializer.data)

    def list(self, request):
        queryset = self.get_queryset()

        if queryset.exists():
            serializer = ReservationSerializer(queryset, many=True)
            return Response({"reservations": serializer.data})
        else:
            return Response({"message": "No reservations found."})

    def create(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Du må være logget inn for å opprette en reservasjon."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            # Overriding the state to PENDING, if needed
            serializer.validated_data["state"] = "PENDING"
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        if not is_admin_user(request):
            return Response(
                {"detail": "Du har ikke tillatelse til å oppdatere reservasjonen."},
                status=status.HTTP_403_FORBIDDEN,
            )
        queryset = self.get_queryset()
        reservation = get_object_or_404(queryset, pk=pk)
        serializer = ReservationSerializer(reservation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE: Delete an existing reservation by its primary key
    def destroy(self, request, pk=None):
        if not is_admin_user(request):
            return Response(
                {"detail": "Du har ikke tillatelse til å slette reservasjonen."},
                status=status.HTTP_403_FORBIDDEN,
            )
        queryset = self.get_queryset()
        reservation = get_object_or_404(queryset, pk=pk)
        reservation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
