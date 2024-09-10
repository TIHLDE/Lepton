from rest_framework import serializers

from app.kontres.models import Reservation, BookableItem
from app.kontres.serializer import BookableItemSerializer
from app.group.models import Group
from app.group.serializers import GroupSerializer
from app.content.models import User
from app.content.serializers import UserSerializer


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
        model: Reservation
        fields = "__all__"

    def validate(self, data):
        return None
