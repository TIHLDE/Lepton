from app.common.serializers import BaseModelSerializer
from app.content.serializers.event import EventListSerializer
from app.gallery.models.album import Album


class AlbumSerializer(BaseModelSerializer):

    event = EventListSerializer(read_only=True)

    class Meta:
        model = Album
        fields = [
            "id",
            "title",
            "event",
            "image",
            "slug",
            "image_alt",
            "description",
        ]
