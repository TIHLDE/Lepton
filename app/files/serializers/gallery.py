from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import DefaultUserSerializer
from app.files.models.gallery import Gallery


class GallerySerializer(BaseModelSerializer):
    author = DefaultUserSerializer(read_only=True)

    class Meta:
        model = Gallery
        fields = (
            "id",
            "created_at",
            "updated_at",
            "author",
        )

    def create_gallery(self, user):
        return Gallery.objects.create(author=user)
