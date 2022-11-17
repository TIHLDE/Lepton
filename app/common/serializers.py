from rest_framework import serializers

from app.common.file_handler import replace_file


class BaseModelSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        if hasattr(instance, "image") and instance.image != validated_data.get("image"):
            replace_file(instance.image, validated_data.get("image", None))
        return super().update(instance, validated_data)
