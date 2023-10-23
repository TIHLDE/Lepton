from app.blitzed.models.drinking_game import DrinkingGame
from app.common.serializers import BaseModelSerializer


class DrinkingGameSerializer(BaseModelSerializer):
    class Meta:
        model = DrinkingGame
        fields = (
            "id",
            "name",
            "description",
            "icon",
        )
