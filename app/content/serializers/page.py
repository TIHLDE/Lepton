from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from app.common.mixins import OrderedModelSerializerMixin
from app.common.serializers import BaseModelSerializer
from app.content.models import Page


class PageSerializer(BaseModelSerializer, OrderedModelSerializerMixin):
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
            "order",
        )

    def get_children(self, obj):
        return [PageListSerializer(page).data for page in obj.get_children()]

    def get_path(self, obj):
        return obj.get_path()


class PageListSerializer(BaseModelSerializer):
    path = SerializerMethodField()

    class Meta:
        model = Page
        fields = ("slug", "title", "path", "order")

    def get_path(self, obj):
        return obj.get_path()


class PageTreeSerializer(serializers.ModelSerializer):
    children = SerializerMethodField()

    class Meta:
        model = Page
        fields = ["slug", "title", "order", "children"]

    def get_children(self, obj):
        return [PageTreeSerializer(page).data for page in obj.get_children()]
