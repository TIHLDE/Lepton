# create_reservation.py or serializers.py
from rest_framework import serializers
from app.kontres.models.reservation import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'
