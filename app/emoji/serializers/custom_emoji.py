from wsgiref import validate
from app.common.serializers import BaseModelSerializer
from rest_framework.serializers import RelatedField
from django.db import transaction
from app.emoji.models import CustomEmoji
from app.emoji.models.custom_short_name import CustomShortName


class CustomShortNameField(RelatedField):
    def to_internal_value(self, data):
        return CustomShortName(value=data)

    def to_representation(self, value):
        return value


class CustomEmojiSerializer(BaseModelSerializer):
    short_names = CustomShortNameField(many=True, queryset=CustomShortName.objects)

    class Meta:
        model = CustomEmoji
        fields = ("img", "short_names")

    @transaction.atomic
    def create(self, validated_data):
        short_names = validated_data.pop("short_names")
        custom_emoji = CustomEmoji.objects.create(**validated_data)
        for short_name in short_names:
            short_name.emoji = custom_emoji
            short_name.save()
        return custom_emoji
