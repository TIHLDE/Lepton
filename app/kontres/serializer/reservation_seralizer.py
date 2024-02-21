from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from app.group.models import Group
from app.kontres.enums import ReservationStateEnum
from app.kontres.models.bookable_item import BookableItem
from app.kontres.models.reservation import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    bookable_item = serializers.PrimaryKeyRelatedField(
        queryset=BookableItem.objects.all()
    )
    group = serializers.SlugRelatedField(slug_field='slug', queryset=Group.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Reservation
        fields = "__all__"

    def validate_start_time(self, start_time):
        if start_time < timezone.now():
            raise serializers.ValidationError("Start-tiden kan ikke være i fortiden.")
        return start_time

    def validate(self, data):

        user = self.context["request"].user

        if 'group' in data and self.instance and data['group'] != self.instance.group:

            # Allow HS or Index members to change the group regardless of the reservation state
            # Other users can only change the group if the reservation state is PENDING
            if not user.is_HS_or_Index_member and self.instance.state != ReservationStateEnum.PENDING:
                raise serializers.ValidationError({
                    "group": "Only HS or Index members can change the group of a non-PENDING reservation."
                })

        if 'group' in data:
            group = data['group']
            if not user.is_member_of(group):
                raise serializers.ValidationError({
                    "group": f"Du er ikke medlem av {group.slug} og kan dermed ikke legge inn "
                             "bestilling på deres vegne."
                })

        # Extract the bookable_item, start_time, and end_time, accounting for the possibility they may not be provided
        bookable_item = data.get(
            "bookable_item", self.instance.bookable_item if self.instance else None
        )

        # Validate the state change permission
        if "state" in data:
            if self.instance and data["state"] != self.instance.state:
                if not (user and user.is_authenticated and user.is_HS_or_Index_member):
                    raise serializers.ValidationError(
                        {
                            "state": "Du har ikke rettigheter til å endre reservasjonsstatusen."
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
            raise serializers.ValidationError("Slutt-tid må være etter start-tid")

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
                    "Det er en reservasjonsoverlapp for det gitte tidsrommet."
                )

        return data
