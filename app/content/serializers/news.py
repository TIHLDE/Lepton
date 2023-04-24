from app.common.serializers import BaseModelSerializer
from app.content.models import News, User
from app.content.serializers.user import DefaultUserSerializer
from app.emoji.serializers.user_news_reaction import UserNewsReactionSerializer


class SimpleNewsSerializer(BaseModelSerializer):
    class Meta:
        model = News
        fields = (
            "id",
            "created_at",
            "updated_at",
            "image",
            "image_alt",
            "title",
            "header",
        )


class NewsSerializer(SimpleNewsSerializer):
    creator = DefaultUserSerializer(read_only=True)
    user_reactions = UserNewsReactionSerializer(
        many=True, required=False, read_only=True
    )

    class Meta:
        model = SimpleNewsSerializer.Meta.model
        fields = SimpleNewsSerializer.Meta.fields + (
            "creator",
            "body",
            "user_reactions",
        )

    def create(self, validated_data):
        creator = self.context["request"].data.get("creator", None)
        if creator:
            creator = User.objects.get(user_id=creator)
        return News.objects.create(creator=creator or None, **validated_data)

    def update(self, instance, validated_data):
        creator = self.context["request"].data.get("creator", None)
        if creator:
            creator = User.objects.get(user_id=creator)

        instance.creator = creator
        return super().update(instance, validated_data)
