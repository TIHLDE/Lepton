from rest_framework import serializers

from dry_rest_permissions.generics import DRYPermissionsField

from ..models import News


class NewsSerializer(serializers.ModelSerializer):
    permissions = DRYPermissionsField()

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
            "body",
            "permissions",
        )
