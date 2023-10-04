from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from app.kontres.serializer.reservation_seralizer import ReservationSerializer
from app.kontres.models.reservation import Reservation
from django.core.exceptions import ObjectDoesNotExist


@api_view(['GET'])
def fetch_reservation(request, reservation_id):
    try:
        if not reservation_id:
            return Response({"error": "Reservation ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        reservation = Reservation.objects.get(id=reservation_id)
        serializer = ReservationSerializer(reservation, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        return Response({"error": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND)

