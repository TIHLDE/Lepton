from rest_framework import serializers

from .models import Item, News, Event


class NewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = News
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        if hasattr(instance, 'news'):
            return NewsSerializer(instance.news).data
        elif hasattr(instance, 'event'):
            return EventSerializer(instance.event).data

    class Meta:
        model = Item
        fields = '__all__'
