from rest_framework import serializers
from app.content.models import User
from app.kontres.models import BookableItem


class BookableItemSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookableItem
        fields = [
            "id", "name", "description"
        ]

class BookableItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookableItem
        fields = "__all__"

class BookableItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookableItem
        fields = [
             "name", "description", "allows_alcohol"         
        ]

    def create(self, validated_data):
        # Get the user which is creating the bookable item
        id = self.context["request"].data.get("creator", None)
        user_object = None
        if id:
            user_object = User.objects.get(user_id=id)
            
        # Create the item in database, return the created object
        return BookableItem.objects.create(creator=user_object, **validated_data)