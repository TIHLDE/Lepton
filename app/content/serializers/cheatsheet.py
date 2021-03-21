from app.common.serializers import BaseModelSerializer

from ..models import Cheatsheet


class CheatsheetSerializer(BaseModelSerializer):
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
