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

    def validate_state(self, value):
        # If the instance exists and the state is being modified
        if self.instance and self.instance.state != value:
            if not self.context["request"].user.is_HS_or_Index_member:
                raise serializers.ValidationError(
                    "You cannot change the state of the reservation."
                )
        return value
