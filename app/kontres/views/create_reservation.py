# views.py

from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from app.kontres.serializer.reservation_seralizer import ReservationSerializer


@api_view(['GET', 'POST'])
def create_reservation(request):
    if request.method == 'GET':
        return Response({"message": "Hello, World!"})

    elif request.method == 'POST':
        serializer = ReservationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)