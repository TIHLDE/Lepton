from rest_framework import serializers

from app.communication.models import Warning


class WarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warning
        fields = "__all__"
