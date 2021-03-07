from rest_framework import serializers

from app.career.models import WeeklyBusiness


class WeeklyBusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyBusiness
        fields = (
            "id",
            "created_at",
            "updated_at",
            "image",
            "image_alt",
            "business_name",
            "body",
            "year",
            "week",
        )
        validators = []
