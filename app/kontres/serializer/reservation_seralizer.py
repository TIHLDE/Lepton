from rest_framework import serializers

from app.kontres.models.bookable_item import BookableItem
from app.kontres.models.reservation import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    bookable_item = serializers.PrimaryKeyRelatedField(
        queryset=BookableItem.objects.all()
    )

    class Meta:
        model = Reservation
        fields = "__all__"
