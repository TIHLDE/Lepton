from rest_framework import serializers

from app.blitzed.models.drinking_game import DrinkingGame
from app.blitzed.models.question import Question
from app.common.serializers import BaseModelSerializer


class DrinkingGameSerializer(BaseModelSerializer):
    questions = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all(), many=True
    )

    class Meta:
        model = DrinkingGame
        fields = (
            "id",
            "name",
            "description",
            "questions",
            "image",
        )
