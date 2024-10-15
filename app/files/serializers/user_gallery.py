from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import DefaultUserSerializer
from app.files.models.user_gallery import UserGallery


class UserGallerySerializer(BaseModelSerializer):
    author = DefaultUserSerializer(read_only=True)

    class Meta:
        model = UserGallery
        fields = (
            "id",
            "created_at",
            "updated_at",
            "author",
        )

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["author"] = user

        return super().create(validated_data)
