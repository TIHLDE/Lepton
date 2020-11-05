from rest_framework import serializers

from ..models import Cheatsheet


class CheatsheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cheatsheet
        fields = [
            "id",
            "title",
            "creator",
            "grade",
            "study",
            "course",
            "type",
            "official",
            "url",
        ]
