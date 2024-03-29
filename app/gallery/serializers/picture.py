from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.gallery.models.album import Album
from app.gallery.models.picture import Picture


class ListPictureSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        id = self.context["id"]
        album = Album.objects.get(id=id)

        pictures = [Picture(album=album, **data) for data in validated_data]
        return Picture.objects.bulk_create(pictures)


class PictureSerializer(BaseModelSerializer):
    class Meta:
        model = Picture
        list_serializer_class = ListPictureSerializer
        fields = (
            "id",
            "image",
            "title",
            "image_alt",
            "description",
            "created_at",
            "updated_at",
        )
