from app.common.serializers import BaseModelSerializer
from app.gallery.models.picture import Album, Picture


class AlbumSerializer(BaseModelSerializer):
    class Meta:
        model = Album
        fields = [
            'title',
            'description',
            'event',
        ]

class PictureSerializer(BaseModelSerializer):
    class Meta:
        model = Picture
        fields = (
            "id",
            "picture",
            "title",
            "description",
            "picture_alt",
            "created_at",
            "updated_at",
        )
