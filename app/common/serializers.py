from rest_framework import serializers

from app.common.file_handler import replace_file


class BaseModelSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        if hasattr(instance, "image") and "image" in validated_data:
            replace_file(instance.image, validated_data.get("image", None))
        if hasattr(instance, "file") and "file" in validated_data:
            replace_file(instance.file, validated_data.get("file", None))
        return super().update(instance, validated_data)
