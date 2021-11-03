from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from app.common.serializers import BaseModelSerializer
from app.content.models import Page


class PageSerializer(BaseModelSerializer):
    children = SerializerMethodField()
    path = SerializerMethodField()
    position = SerializerMethodField()

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
            "position",
        )

    def get_children(self, obj):
        children = [PageListSerializer(page).data for page in obj.get_children()]
        return sorted(children, key=lambda child: child["position"])

    def get_path(self, obj):
        return obj.get_path()

    def get_position(self, obj):
        return obj.get_position()

            

class PageListSerializer(BaseModelSerializer):
    path = SerializerMethodField()
    position = SerializerMethodField()

    class Meta:
        model = Page
        fields = (
            "slug",
            "title",
            "path",
            "position"
        )

    def get_path(self, obj):
        return obj.get_path()

    def get_position(self, obj):
        return obj.get_position()


class PageTreeSerializer(serializers.ModelSerializer):
    children = SerializerMethodField()
    position = SerializerMethodField()

    class Meta:
        model = Page
        fields = ["slug", "title","position", "children"]

    def get_children(self, obj):
        children = [PageTreeSerializer(page).data for page in obj.get_children()]
        return sorted(children, key=lambda child: child["position"])

    def get_position(self, obj):
        return obj.get_position()