from rest_framework import serializers

from app.content.models.comment import Comment
from app.content.models.event import Event
from app.content.models.news import News
from app.content.serializers.user import DefaultUserSerializer
from app.content.enums import ContentType


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
            "indent_level",
            "parent",
            "children"
        )

    def to_representation(self, instance):
        self.fields["children"] = CommentSerializer(many=True, read_only=True)
        return super(CommentSerializer, self).to_representation(instance)


class CommentCreateSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField()
    content_id = serializers.IntegerField()

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
        content_type = validated_data.pop("content_type")
        content_id = validated_data.pop("content_id")
        author = validated_data.pop("author")
        body = validated_data.pop("body")
        parent = validated_data.pop("parent")

        if parent and parent.indent_level >= 3:
            # TODO: make exception for many indents in thread
            raise Exception("For mange kommentarer i tråden.")

        if content_type == ContentType.EVENT:
            event = Event.objects.get(id=content_id)

            if parent:
                created_comment = event.comments.create(
                    author=author,
                    body=body,
                    parent=parent,
                    indent_level=parent.indent_level + 1
                )
                return created_comment

            created_comment = event.comments.create(
                author=author,
                body=body
            )
            return created_comment
        
        if content_type == ContentType.NEWS:
            news = News.objects.get(id=content_id)

            if parent:
                created_comment = news.comments.create(
                    author=author,
                    body=body,
                    parent=parent,
                    indent_level=parent.indent_level + 1
                )

            created_comment = news.comments.create(
                author=author,
                body=body
            )
            return created_comment


class CommentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = (
            "id",
            "body"
        )

    def update(self, instance, validated_data):
        comment = super().update(instance, validated_data)
        comment.save()

        return comment