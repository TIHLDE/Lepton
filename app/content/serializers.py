from rest_framework import serializers

from .models import (News, Event,
                     Warning, Category, JobPost, User, UserEvent)
from ..authentication.models import Connection

from ..authentication.models import Connection

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
    events = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'user_id',
            'first_name',
            'last_name',
            'email',
            'cell',
            'em_nr',
            'home_busstop',
            'gender',
            'user_class',
            'user_study',
            'allergy',
            'tool',
            'events',
            'groups'
            )
        extra_kwargs = {
            'user_id': {'read_only': True},
            'first_name': {'read_only': True},
            'last_name': {'read_only': True},
            'email': {'read_only': True}
        }
    
    def get_events(self, obj):
        """
            Lists all events user is to attend or has attended
            :param obj: the current user object
            :return: a list of serialized events 
        """
        user_events = UserEvent.objects.filter(user__user_id=obj.user_id)
        events = [user_event.event for user_event in user_events]
        return EventSerializer(events, many=True).data
    
    def get_groups(self, obj):
        connections = [Connection.objects.filter(user_id=obj.user_id)]
        return [connection.group.name for connection in connections]

    def get_groups(self, obj):
        connections = Connection.objects.filter(user_id=obj.user_id)
        return [connection.group.name for connection in connections]


class UserEventSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField()
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = UserEvent
        fields = ['user_event_id', 'user_id', 'user_info', 'is_on_wait', 'has_attended']

    def get_user_info(self, obj):
        user = User.objects.get(user_id=obj.user_id)
        return { 
            'first_name': user.first_name,
            'last_name': user.last_name, 
            'user_class': user.user_class,
            'user_study': user.user_study,
            'allergy': user.allergy
        }


class EventSerializer(serializers.ModelSerializer):
    expired = serializers.BooleanField(read_only=True)
    registered_users_list = serializers.SerializerMethodField()
    registered_users_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'start', 'location', 
            'description', 'sign_up', 'priority', 
            'category', 'expired', 'limit', 'closed', 
            'registered_users_list', 'registered_users_count', 
            'image', 'image_alt'
        ]

    def get_registered_users_count(self, obj):
        """ Number of users registered for the event """
        return obj.registered_users_list.count()

    def get_registered_users_list(self, obj):
        """ Return only some user fields"""
        try:
            return [{
                'user_id': user.user_id, 
                'first_name': user.first_name, 
                'last_name': user.last_name
                } for user in obj.registered_users_list.all()]        
        except User.DoesNotExist:
            return None
