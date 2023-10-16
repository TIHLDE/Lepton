from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from app.kontres.serializer.reservation_seralizer import ReservationSerializer
from app.kontres.models.reservation import Reservation
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError, ObjectDoesNotExist


@api_view(['GET', 'POST', 'PUT'])
def reservation_view(request, reservation_id=None):
    # Create a reservation
    if request.method == 'POST':
        print(request.data)
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.validated_data['state'] = 'PENDING'
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Edit a reservation
    elif request.method == 'PUT':
        if not reservation_id:
            return Response({"error": "No reservation id provided"}, status=status.HTTP_400_BAD_REQUEST)

        reservation = get_object_or_404(Reservation, id=reservation_id)
        serializer = ReservationSerializer(reservation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Fetch all or one reservation
    elif request.method == 'GET':
        if reservation_id:
            try:
                reservation = Reservation.objects.get(id=reservation_id)
                serializer = ReservationSerializer(reservation, many=False)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({"error": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
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
                return Response({"reservations": serializer.data})
            else:
                return Response({"message": "No reservations found."})
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
