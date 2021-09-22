from rest_framework import serializers

from app.gallery.models import Picture


class PictureSerializer(serializers.ModelSerializer):
    class Meta():
        model = Picture
        fields = (
            "picture",
            #"event",
            "title",
            "description",
            "picture_alt",
            "created_at",
            "updated_at",
        )

