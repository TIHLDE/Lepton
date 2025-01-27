from app.common.serializers import BaseModelSerializer
from app.content.serializers.user import SimpleUserSerializer
from app.feedback.models.idea import Idea


class IdeaSerializer(BaseModelSerializer):
    author = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Idea
        fields = (
            "id",
            "title",
            "status",
            "created_at",
            "author",
            "description",
            "image",
            "image_alt",
        )


class IdeaCreateSerializer(BaseModelSerializer):
    class Meta:
        model = Idea
        fields = (
            "title",
            "description",
            "image",
            "image_alt",
        )

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["author"] = user

        return super().create(validated_data)


class IdeaUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = Idea
        fields = (
            "title",
            "description",
            "status",
            "image",
            "image_alt",
        )

        def update(self, instance, validated_data):
            return super().update(instance, validated_data)


class IdeaDetailSerializer(BaseModelSerializer):
    author = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Idea
        fields = (
            "id",
            "title",
            "description",
            "status",
            "created_at",
            "author",
            "image",
            "image_alt",
        )
