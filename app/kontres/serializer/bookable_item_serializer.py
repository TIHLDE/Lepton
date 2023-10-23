# serializers/bookable_item_serializer.py

from rest_framework import serializers

from kontres.models.bookable_item import BookableItem


class BookableItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookableItem
        fields = "__all__"
