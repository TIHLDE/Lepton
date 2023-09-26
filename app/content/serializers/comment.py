from rest_framework import serializers

from app.content.models.comment import Comment
from app.content.models.event import Event
from app.content.serializers.user import DefaultUserSerializer

class CommentSerializer(serializers.ModelSerializer):
    author = DefaultUserSerializer(read_only=True, required=False)

    class Meta:
        model = Comment
        fields = (
            "id",
            "body",
            "created_at",
            "updated_at",
            "author",
            "parent"
        )


class CommentCreateAndUpdateSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField()
    content_id = serializers.FloatField()

    class Meta:
        model = Comment
        fields = (
            "body",
            "author",
            "parent",
            "content_type",
            "content_id"
        )

    def create(self, validated_data):
        print("inside create")
        print(validated_data)
        content_type = validated_data.pop("content_type")
        content_id = validated_data.pop("content_id")
        author = validated_data.pop("author")
        body = validated_data.pop("body")

        if content_type == "event":
            event = Event.objects.get(id=int(content_id))
            created_comment = event.comments.create(
                author=author,
                body=body
            )
            print(created_comment)