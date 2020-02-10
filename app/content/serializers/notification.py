from rest_framework import serializers

from ..models import User, Notification

class NotificationSerializer(serializers.ModelSerializer):
    """ Serilaize all the notifcations """
    class Meta:
        model = Notification
        fields = '__all__'
