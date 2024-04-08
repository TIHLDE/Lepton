from rest_framework import serializers

from app.content.models import Minute, User


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("user_id", "first_name", "last_name", "image")


class MinuteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Minute
        fields = ("title", "content")

    def create(self, validated_data):
        author = self.context["request"].user
        minute = Minute.objects.create(**validated_data, author=author)
        return minute


class MinuteSerializer(serializers.ModelSerializer):
    author = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Minute
        fields = ("id", "title", "content", "author", "created_at", "updated_at")


class MinuteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Minute
        fields = ("id", "title", "content")

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
