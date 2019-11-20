from rest_framework import serializers

from ..models import Event, User, UserEvent


class EventSerializer(serializers.ModelSerializer):
    expired = serializers.BooleanField(read_only=True)
    registered_users_list = serializers.SerializerMethodField()
    is_user_registered = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'start', 'location',
            'description', 'sign_up', 'priority',
            'category', 'expired', 'limit', 'closed',
            'registered_users_list', 'list_count',
            'waiting_list_count', 'is_user_registered',
            'image', 'image_alt'
        ]

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
            that the limit can not be lower than the number of registered users.
            If the limit is already 0, then do not let that effect updating other fields
        """
        try:
            if limit < 0:
                raise serializers.ValidationError("Event limit can not a negative integer")
            elif limit < self.instance.registered_users_list.all().count() and self.instance.limit is not 0:
                raise serializers.ValidationError("Event limit can not be lower than number of registered users.")
            return limit
        except AttributeError:
            return limit

    def get_is_user_registered(self, obj):
        """ Check if user loading event is signed up """
        request = self.context.get('request')
        if request and hasattr(request, 'id'):
            user_id = request.id
            return UserEvent.objects.filter(event__pk=obj.pk, user__user_id=user_id).count() > 0
        return None


class EventInUserSerializer(EventSerializer):
    expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'start', 'location', 'priority', 'limit',
            'closed', 'description', 'expired', 'image', 'image_alt'
        ]
