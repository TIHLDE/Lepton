from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.kontres.serializer.reservation_seralizer import ReservationSerializer
from app.kontres.models.reservation import Reservation


@api_view(['GET'])
def fetch_all_reservations(request):
    if request.method == 'GET':
        # Fetching data based on date filters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date == '0' and end_date == '0':
            reservations = Reservation.objects.all()
        elif start_date and end_date:
            reservations = Reservation.objects.filter(start_time__gte=start_date, end_time__lte=end_date)
        else:
            reservations = Reservation.objects.all()

        if reservations.exists():
            serializer = ReservationSerializer(reservations, many=True)
            return Response({
                "reservations": serializer.data,
            })
        else:
            return Response({
                "message": "No reservations found."
            })
