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
        children = [PageListSerializer(page).data for page in obj.get_children()]
        return sorted(children, key=lambda child: child["order"])

    def get_path(self, obj):
        return obj.get_path()


class PageListSerializer(BaseModelSerializer, OrderedModelSerializerMixin):
    path = SerializerMethodField()

    class Meta:
        model = Page
        fields = ("slug", "title", "path", "order")

    def get_path(self, obj):
        return obj.get_path()


class PageTreeSerializer(serializers.ModelSerializer, OrderedModelSerializerMixin):
    children = SerializerMethodField()

    class Meta:
        model = Page
        fields = ["slug", "title", "order", "children"]

    def get_children(self, obj):
        children = [PageTreeSerializer(page).data for page in obj.get_children()]
        return sorted(children, key=lambda child: child["order"])
