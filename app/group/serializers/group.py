from rest_framework import serializers

from app.group.models import Group


class DefaultGroupSerializer(serializers.ModelSerializer):
    """Serizlier for Groups with lookup by slug field and only return the name of the group"""

    class Meta:
        model = Group
        fields = ("name",)


class GroupSerializer(serializers.ModelSerializer):
    """Serizlier for Groups with lookup by slug field"""

    class Meta:
        model = Group
        lookup_field = "slug"
        fields = (
            "name",
            "slug",
            "description",
            "contact_email",
            "type",
            "permissions",
        )
