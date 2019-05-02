from rest_framework import serializers

from .models import (News, Event,
                     Warning, Category, JobPost)

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

class WarningSerializer(serializers.ModelSerializer):

    class Meta:
        model = Warning
        fields = '__all__'  # bad form

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'  # bad form

class JobPostSerializer(serializers.ModelSerializer):

    expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = JobPost
        fields = '__all__'  # bad form
