# create_reservation.py or serializers.py
from rest_framework import serializers
from app.kontres.models.reservation import Reservation
from app.kontres.serializer.bookable_item_serializer import BookableItemSerializer


class ReservationSerializer(serializers.ModelSerializer):
    bookable_item = BookableItemSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = '__all__'
