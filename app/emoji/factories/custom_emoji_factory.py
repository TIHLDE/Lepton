import factory
from factory.django import DjangoModelFactory

from app.emoji.models.custom_emoji import CustomEmoji


class CustomEmojiFactory(DjangoModelFactory):
    class Meta:
        model = CustomEmoji

    img = factory.Faker("url")
