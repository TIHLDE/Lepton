from rest_framework import serializers

from app.kontresv2.models.bookable_item import BookableItem


class BookableItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookableItem
        fields = "__all__"
