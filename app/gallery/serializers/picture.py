from app.common.serializers import BaseModelSerializer
from app.gallery.models.picture import Picture


class PictureSerializer(BaseModelSerializer):
    class Meta:
        model = Picture
        fields = (
            "id",
            "image",
            "title",
            "description",
            "image_alt",
            "created_at",
            "updated_at",
        )
