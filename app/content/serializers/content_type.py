from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from app.common.serializers import BaseModelSerializer


class ContentTypeSerializer(BaseModelSerializer):
    app_label_name = serializers.SerializerMethodField()

    class Meta:
        model = ContentType
        fields = ("app_label_name",)

    def get_app_label_name(self, obj):
        return obj.app_labeled_name
