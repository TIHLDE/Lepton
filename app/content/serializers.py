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
        representation = None
        if hasattr(instance, 'news'):
            representation = NewsSerializer(instance.news).data
            representation['type'] = 'news'
        elif hasattr(instance, 'event'):
            representation = EventSerializer(instance.event).data
            representation['type'] = 'event'
        return representation

    class Meta:
        model = Item
        fields = '__all__'
