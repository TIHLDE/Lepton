from rest_framework import serializers

from .models import (News, Event,
                     Warning, Category, JobPost, User, UserEvent)

from logzero import logger


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'  # bad form


class EventSerializer(serializers.ModelSerializer):
    expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'start', 'location', 'description', 'sign_up', 'priority', 'category', 'expired', 'limit', 'closed', 'registered_users_list', 'image', 'image_alt']

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

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'cell', 'em_nr', 'home_busstop', 'gender', 'user_class', 'user_study', 'allergy', 'tool']

class UserEventSerializer(serializers.ModelSerializer):

    # user_id = serializers.CharField() # makes it possible to add by name

    class Meta:
        model = UserEvent
        fields = ['event', 'user', 'is_on_wait', 'has_attended']