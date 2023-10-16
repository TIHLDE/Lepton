from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from app.kontres.models.reservation import Reservation  # Replace with the actual path to your model
from app.kontres.serializer.reservation_seralizer import ReservationSerializer


class ReservationViewSet(viewsets.ViewSet):

    # GET: Retrieve a single reservation by its primary key
    def retrieve(self, request, pk=None):
        queryset = Reservation.objects.all()
        reservation = get_object_or_404(queryset, pk=pk)
        serializer = ReservationSerializer(reservation)
        return Response(serializer.data)

    # GET: Retrieve a list of all reservations
    def list(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date == '0' and end_date == '0':
            queryset = Reservation.objects.all()
        elif start_date and end_date:
            queryset = Reservation.objects.filter(start_time__gte=start_date, end_time__lte=end_date)
        else:
            queryset = Reservation.objects.all()

        if queryset.exists():
            serializer = ReservationSerializer(queryset, many=True)
            return Response({"reservations": serializer.data})
        else:
            return Response({"message": "No reservations found."})

    # POST: Create a new reservation
    def create(self, request):
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            # Overriding the state to PENDING, if needed
            serializer.validated_data['state'] = 'PENDING'
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT: Update an existing reservation by its primary key
    def update(self, request, pk=None):
        queryset = Reservation.objects.all()
        reservation = get_object_or_404(queryset, pk=pk)
        serializer = ReservationSerializer(reservation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE: Delete an existing reservation by its primary key
    def destroy(self, request, pk=None):
        queryset = Reservation.objects.all()
        reservation = get_object_or_404(queryset, pk=pk)
        reservation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
