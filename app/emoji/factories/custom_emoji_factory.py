import factory
from factory.django import DjangoModelFactory
from app.emoji.models.custom_emoji import CustomEmoji
from django.core.files.base import ContentFile


class CustomEmojiFactory(DjangoModelFactory):
    class Meta:
        model = CustomEmoji

    img = factory.Faker("url")