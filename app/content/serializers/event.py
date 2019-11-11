from rest_framework import serializers

from ..models import Event, User


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
    def validate_limit(self, limit):
        """
            Check that the event limit is greater or equal to 0 and
            that the limit can not be lower than the number of registered users
        """
        try:
            if limit < 0:
                raise serializers.ValidationError("Event limit can not a negative integer")
            elif limit <= self.get_registered_users_count(self.instance):
                raise serializers.ValidationError("Event limit can not be lower than number of registered users.")
            return limit
        except AttributeError:
            return limit




class EventInUserSerializer(EventSerializer):
    expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'start', 'location', 'priority', 'limit',
            'closed', 'description', 'expired', 'image', 'image_alt'
        ]
