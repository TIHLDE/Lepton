from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from app.kontres.serializer.reservation_seralizer import ReservationSerializer
from app.kontres.models.reservation import Reservation
from django.shortcuts import get_object_or_404


@api_view(['PUT'])
def edit_reservation(request, reservation_id):
    # TODO: Add validation for the request

    if not reservation_id:
        return Response({"error": "No reservation id provided"}, status=status.HTTP_400_BAD_REQUEST)

    # if not request.user.is_staff:
    #     return Response({"error": "You are not authorized to edit this reservation"},
    #                     status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'PUT':
        reservation = get_object_or_404(Reservation, id=reservation_id)
        serializer = ReservationSerializer(reservation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
