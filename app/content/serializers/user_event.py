from rest_framework import serializers

from ..models import User, UserEvent


class UserEventSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField()
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = UserEvent
        fields = ['user_event_id', 'user_id', 'user_info', 'is_on_wait', 'has_attended']

    def get_user_info(self, obj):
        """ Gets the necessary info from user """
        user = User.objects.get(user_id=obj.user_id)
        return {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_class': user.user_class,
            'user_study': user.user_study,
            'allergy': user.allergy
        }


