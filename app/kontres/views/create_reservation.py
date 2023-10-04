from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from app.kontres.serializer.reservation_seralizer import ReservationSerializer
from django.core.exceptions import ValidationError


@api_view(['POST'])
def create_reservation(request):
    if request.method == 'POST':
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Override the state to always be 'PENDING'
                serializer.validated_data['state'] = 'PENDING'

                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
