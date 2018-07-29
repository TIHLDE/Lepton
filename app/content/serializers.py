from rest_framework import serializers

from .models import Item, News, Event, EventList, Poster, ImageGallery, Image

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class EventListSerializer(serializers.ModelSerializer):
    events = EventSerializer(many=True, read_only=True)
    class Meta:
        model = EventList
        fields = '__all__'

class PosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poster
        fields = '__all__'

class ItemBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class ImageGallerySerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    class Meta:
        model = ImageGallery
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = ItemBaseSerializer(instance).data

        exclude = set(representation)

        types = [
            ('news', NewsSerializer),
            ('eventlist', EventListSerializer),
            ('poster', PosterSerializer)
        ]

        type = None
        for t in types:
            if hasattr(instance, t[0]):
                type = t
                break

        datarep = type[1](getattr(instance, type[0])).data
        representation['data'] = {f: datarep[f] for f in datarep if f not in exclude and datarep[f]}
        representation['type'] = type[0]

        return representation

    class Meta:
        model = Item
        fields = '__all__'
        depth = 1
