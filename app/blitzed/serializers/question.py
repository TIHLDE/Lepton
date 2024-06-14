from app.blitzed.models.question import Question
from app.common.serializers import BaseModelSerializer


class QuestionSerializer(BaseModelSerializer):
    class Meta:
        model = Question
        fields = (
            "id",
            "text",
            "drinking_game",
        )
