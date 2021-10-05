from app.common.serializers import BaseModelSerializer
from app.gallery.models.picture import Picture


class PictureSerializer(BaseModelSerializer):
    class Meta:
        model = Picture
        fields = (
            "picture",
            "event",
            "title",
            "description",
            "picture_alt",
            "created_at",
            "updated_at",
        )
