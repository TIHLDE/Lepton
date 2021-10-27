from app.common.serializers import BaseModelSerializer
from app.gallery.models.album import Album
from app.gallery.models.picture import Picture
from rest_framework import serializers


class ListPictureSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        album_id = self.context["slug"]
        album = Album.objects.get(slug=album_id)

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
