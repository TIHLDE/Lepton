from rest_framework import serializers

from .models import (Item, News, Event, EventList,
                     Poster, Grid, ManualGrid, RecentFirstGrid,
                     ImageGallery, Image, Warning, Category)

from logzero import logger


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'  # bad form


class EventSerializer(serializers.ModelSerializer):

    expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'start', 'location', 'eventlist', 'description', 'sign_up', 'priority', 'category', 'expired', 'image', 'image_alt']


class EventListSerializer(serializers.ModelSerializer):
    events = serializers.SerializerMethodField()

    class Meta:
        model = EventList
        fields = '__all__'  # bad form

    def get_events(self, list):
        events = (e for e in Event.objects.filter(eventlist=list) if not e.expired())
        serializer = EventSerializer(instance=events, many=True)
        return serializer.data


class PosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poster
        fields = '__all__'  # bad form


class ItemBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'  # bad form


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'  # bad form


class ImageGallerySerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = ImageGallery
        fields = '__all__'  # bad form


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
        fields = '__all__'  # bad form
        depth = 1


class GridBaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Grid
        fields = '__all__'  # bad form


class ManualGridSerializer(serializers.ModelSerializer):

    items = ItemSerializer(many=True)

    class Meta:
        model = ManualGrid
        fields = '__all__'  # bad form


class RecentFirstGridSerializer(serializers.ModelSerializer):

    items = ItemSerializer(many=True)

    class Meta:
        model = RecentFirstGrid
        fields = '__all__'  # bad form


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
        fields = '__all__'  # bad form


class WarningSerializer(serializers.ModelSerializer):

    class Meta:
        model = Warning
        fields = '__all__'  # bad form

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'  # bad form
