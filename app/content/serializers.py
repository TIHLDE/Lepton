from rest_framework import serializers

from .models import (News, Event,
                     Warning, Category, JobPost, User, UserEvent)

from logzero import logger


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'  # bad form

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
    user_id = serializers.CharField() # makes it possible to add by user id

    class Meta:
        model = UserEvent
        fields = ['user_event_id', 'user_id', 'event', 'is_on_wait', 'has_attended']

class EventSerializer(serializers.ModelSerializer):
    expired = serializers.BooleanField(read_only=True)
    registered_users_list = serializers.SerializerMethodField() # Fix: not send every time

    class Meta:
        model = Event
        fields = ['id', 'title', 'start', 'location', 'description', 'sign_up', 'priority', 'category', 'expired', 'limit', 'closed', 'registered_users_list', 'image', 'image_alt']

    def get_registered_users_list(self, obj):
        """ Check permission/ownership of event """
        if self.context['request'].user.is_authenticated:
            try:
                return [str(item) for item in obj.registered_users_list.all()]
            except User.DoesNotExist:
                return None
        return None