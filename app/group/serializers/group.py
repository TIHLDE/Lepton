from rest_framework import serializers

from app.group.models import Group


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
