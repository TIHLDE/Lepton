from rest_framework import serializers

from app.content.models import Strike


class StrikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strike
        fields = (
            "description",
            "nr_of_strikes",
            "expires_at",
        )


