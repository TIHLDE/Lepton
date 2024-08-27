from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from app.content.models import User
from app.content.serializers import UserSerializer
from app.group.models import Group
from app.group.serializers import GroupSerializer
from app.kontres.enums import ReservationStateEnum
from app.kontres.models.bookable_item import BookableItem
from app.kontres.models.reservation import Reservation
from app.kontres.serializer.bookable_item_serializer import (
    BookableItemSerializer,
)


class ReservationSerializer(serializers.ModelSerializer):
    bookable_item = serializers.PrimaryKeyRelatedField(
        queryset=BookableItem.objects.all(), write_only=True, required=False
    )
    bookable_item_detail = BookableItemSerializer(
        source="bookable_item", read_only=True
    )
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), write_only=True, required=False
    )
    group_detail = GroupSerializer(source="group", read_only=True)

    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False
    )
    author_detail = UserSerializer(source="author", read_only=True)

    sober_watch = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False
    )
    sober_watch_detail = UserSerializer(source="sober_watch", read_only=True)

    approved_by_detail = UserSerializer(source="approved_by", read_only=True)

    class Meta:
        model = Reservation
        fields = "__all__"

    def validate(self, data):
        user = self.context["request"].user
        group = data.get("group", None)

        bookable_item = (
            data.get("bookable_item")
            if "bookable_item" in data
            else self.instance.bookable_item
        )

        if group:
            self.validate_group(group)

        if bookable_item.allows_alcohol:
            self.validate_alcohol(data)

        self.validate_state_change(data, user)
        self.validate_time_and_overlapping(data)
        return data

    def validate_alcohol(self, data):
        if data.get(
            "serves_alcohol",
            self.instance.serves_alcohol if self.instance else False,
        ):
            sober_watch = data.get(
                "sober_watch", self.instance.sober_watch if self.instance else None
            )
            if (
                not sober_watch
                or not User.objects.filter(user_id=sober_watch.user_id).exists()
            ):
                raise serializers.ValidationError(
                    "Du må velge en edruvakt for reservasjonen."
                )

    def validate_group(self, value):
        user = self.context["request"].user
        group = value

        if self.instance and group != self.instance.group:
            if (
                not user.is_HS_or_Index_member
                and self.instance.state != ReservationStateEnum.PENDING
            ):
                raise serializers.ValidationError(
                    "Du har ikke tilgang til å endre gruppen til denne reservasjonsforespørselen."
                )

        if group and not user.is_member_of(group):
            raise serializers.ValidationError(
                f"Du er ikke medlem av {group.slug} og kan dermed ikke legge inn bestilling på deres vegne."
            )

        return group

    def validate_state_change(self, data, user):
        # Validate the state change permission
        if "state" in data:
            if self.instance and data["state"] != self.instance.state:
                if not (user and user.is_authenticated and user.is_HS_or_Index_member):
                    raise serializers.ValidationError(
                        {
                            "state": "Du har ikke rettigheter til å endre reservasjonsstatusen."
                        }
                    )

    def validate_time_and_overlapping(self, data):
        # Check if this is an update operation and if start_time is being modified.
        is_update_operation = self.instance is not None
        start_time_being_modified = "start_time" in data
        state_being_modified = "state_change" in data

        # Retrieve the start and end times from the data if provided, else from the instance.
        start_time = data.get(
            "start_time", self.instance.start_time if self.instance else None
        )
        end_time = data.get(
            "end_time", self.instance.end_time if self.instance else None
        )

        # Skip the past start time check if this is an update and the start time isn't being modified.
        if not (is_update_operation and not start_time_being_modified):
            if start_time < timezone.now():
                raise serializers.ValidationError(
                    "Start-tiden kan ikke være i fortiden."
                )

        # Ensure the end time is after the start time for all operations.
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError("Slutt-tid må være etter start-tid")
        bookable_item = data.get(
            "bookable_item", self.instance.bookable_item if self.instance else None
        )
        # Check for overlapping reservations only if necessary fields are present
        if bookable_item and start_time and end_time and not state_being_modified:
            # Build the query for overlapping reservations
            overlapping_reservations_query = Q(
                bookable_item=bookable_item,
                end_time__gt=start_time,
                start_time__lt=end_time,
                state=ReservationStateEnum.CONFIRMED,
            )
            # Exclude the current instance if updating
            if self.instance:
                overlapping_reservations_query &= ~Q(pk=self.instance.pk)
            # Check for overlapping reservations
            if Reservation.objects.filter(overlapping_reservations_query).exists():
                raise serializers.ValidationError(
                    "Det er en reservasjonsoverlapp for det gitte tidsrommet."
                )
