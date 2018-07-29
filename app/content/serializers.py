from rest_framework import serializers

from .models import (Item, News, Event, EventList,
                     Poster, Grid, ManualGrid, RecentFirstGrid,
                     ImageGallery, Image)

from logzero import logger

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
            ('poster', PosterSerializer),
            ('imagegallery', ImageGallerySerializer),
        ]

        type = None
        for t in types:
            if hasattr(instance, t[0]):
                type = t
                break

        if type:
            datarep = type[1](getattr(instance, type[0])).data
            representation['data'] = {f: datarep[f] for f in datarep if f not in exclude and datarep[f]}
            representation['type'] = type[0]
        else:
            logger.warning('Unable to recognize type for item: {}, are you sure it is in the list of types?'.format(instance))

        return representation

    class Meta:
        model = Item
        fields = '__all__'
        depth = 1

class GridBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grid
        fields = '__all__'

class ManualGridSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)

    class Meta:
        model = ManualGrid
        fields = '__all__'

class RecentFirstGridSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)

    class Meta:
        model = RecentFirstGrid
        fields = '__all__'

class GridSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        # TODO: Remove duplicate code
        representation = GridBaseSerializer(instance).data

        exclude = set(representation)

        types = [
            ('manualgrid', ManualGridSerializer),
            ('recentfirstgrid', RecentFirstGridSerializer),
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
        model = Grid
        fields = '__all__'
