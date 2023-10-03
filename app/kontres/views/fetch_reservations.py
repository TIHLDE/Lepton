from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.kontres.serializer.reservation_seralizer import ReservationSerializer
from app.kontres.models.reservation import Reservation


@api_view(['GET'])
def fetch_all_reservations(request):
    if request.method == 'GET':
        reservations = Reservation.objects.all()
        serializer = ReservationSerializer(reservations, many=True)

        return Response({
            "reservations": serializer.data,
        })
