from django.db.models import Q
from django.utils import timezone
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

    def validate_start_time(self, start_time):
        if start_time < timezone.now():
            raise serializers.ValidationError("The start time cannot be in the past.")
        return start_time

    def validate(self, data):

        # Extract the bookable_item, start_time, and end_time, accounting for the possibility they may not be provided
        bookable_item = data.get(
            "bookable_item", self.instance.bookable_item if self.instance else None
        )

        # Validate the state change permission
        if "state" in data:
            if self.instance and data["state"] != self.instance.state:
                user = self.context["request"].user
                if not (user and user.is_authenticated and user.is_HS_or_Index_member):
                    raise serializers.ValidationError(
                        {
                            "state": "You do not have permission to change the state of the reservation."
                        }
                    )

        # Validate that the end time is after the start time
        start_time = data.get(
            "start_time", self.instance.start_time if self.instance else None
        )
        end_time = data.get(
            "end_time", self.instance.end_time if self.instance else None
        )
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError("end_time must be after start_time")

        # Check for overlapping reservations only if necessary fields are present
        if bookable_item and start_time and end_time:
            # Build the query for overlapping reservations
            overlapping_reservations_query = Q(
                bookable_item=bookable_item,
                end_time__gt=start_time,
                start_time__lt=end_time,
            )
            # Exclude the current instance if updating
            if self.instance:
                overlapping_reservations_query &= ~Q(pk=self.instance.pk)
            # Check for overlapping reservations
            if Reservation.objects.filter(overlapping_reservations_query).exists():
                raise serializers.ValidationError(
                    "There is an overlapping reservation for the selected time frame."
                )

        return data
