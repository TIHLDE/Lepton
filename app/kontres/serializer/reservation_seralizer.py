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
from app.kontres.serializer.bookable_item_serializer import BookableItemSerializer


class ReservationSerializer(serializers.ModelSerializer):
    bookable_item = serializers.PrimaryKeyRelatedField(
        queryset=BookableItem.objects.all(), write_only=True, required=False
    )
    bookable_item_detail = BookableItemSerializer(source='bookable_item', read_only=True)
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), write_only=True, required=False
    )
    group_detail = GroupSerializer(source='group', read_only=True)

    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False
    )
    author_detail = UserSerializer(source='author', read_only=True)

    class Meta:
        model = Reservation
        fields = "__all__"

    def validate(self, data):
        user = self.context["request"].user
        group = data.get("group", None)
        if group:
            self.validate_group(group)
        self.validate_state_change(data, user)
        self.validate_time_and_overlapping(data)
        return data

    def validate_group(self, value):
        user = self.context["request"].user
        group = value

        if self.instance and group != self.instance.group:
            # Assuming your model logic and permissions are correctly implemented in is_HS_or_Index_member
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
        pass

    def validate_time_and_overlapping(self, data):

        # Validate that the end time is after the start time
        start_time = data.get(
            "start_time", self.instance.start_time if self.instance else None
        )
        if start_time < timezone.now():
            raise serializers.ValidationError("Start-tiden kan ikke være i fortiden.")
        end_time = data.get(
            "end_time", self.instance.end_time if self.instance else None
        )
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError("Slutt-tid må være etter start-tid")
        # Extract the bookable_item, start_time, and end_time, accounting for the possibility they may not be provided
        bookable_item = data.get(
            "bookable_item", self.instance.bookable_item if self.instance else None
        )
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
        pass
