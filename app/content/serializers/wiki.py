from rest_framework import serializers

from ..models import WikiPost


class WikiListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WikiPost
        fields = ["slug", "title", "description"]


class WikiPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = WikiPost
        fields = ["slug", "title", "content", "description"]
