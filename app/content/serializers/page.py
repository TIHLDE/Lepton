from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from app.content.models import Page


class PageSerializer(serializers.ModelSerializer):
    children = SerializerMethodField()
    path = SerializerMethodField()

    class Meta:
        model = Page
        fields = (
            "slug",
            "title",
            "content",
            "path",
            "children",
            "created_at",
            "updated_at",
            "image",
            "image_alt",
        )

    def get_children(self, obj):
        return [{"title": page.title, "slug": page.slug} for page in obj.get_children()]

    def get_path(self, obj):
        return obj.get_path()


class PageTreeSerializer(serializers.ModelSerializer):
    children = SerializerMethodField()

    class Meta:
        model = Page
        fields = ["slug", "title", "children"]

    def get_children(self, obj):
        return [PageTreeSerializer(page).data for page in obj.get_children()]
