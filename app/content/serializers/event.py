from rest_framework import serializers

from ..models import Event, User, UserEvent


class EventSerializer(serializers.ModelSerializer):
    expired = serializers.BooleanField(read_only=True)
    registered_users_list = serializers.SerializerMethodField()
    registered_users_count = serializers.SerializerMethodField()
    # TODO: come up with a better name
    is_current_user_signed_up = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'start', 'location',
            'description', 'sign_up', 'priority',
            'category', 'expired', 'limit', 'closed',
            'registered_users_list', 'registered_users_count',
            'is_current_user_signed_up', 'image', 'image_alt'
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

    def get_is_current_user_signed_up(self, obj):
        try:
            user_id = self.context['request'].user.user_id
            return UserEvent.objects.filter(event__pk=obj.pk, user__user_id=user_id).count() > 0
        except AttributeError:
            return False


class EventInUserSerializer(EventSerializer):
    expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'start', 'location', 'priority', 'limit',
            'closed', 'description', 'expired', 'image', 'image_alt'
        ]
