from rest_framework import serializers

from app.content.models import Event, Strike, User


class BaseStrikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strike
        fields = (
            "id",
            "description",
            "nr_of_strikes",
            "expires_at",
        )


class StrikeSerializer(BaseStrikeSerializer):

    user = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()
    creator = serializers.SerializerMethodField()

    class Meta:
        model = Strike
        fields = BaseStrikeSerializer.Meta.fields + ("user", "event", "creator")

    def get_user(self, obj):
        user = User.objects.get(user_id=obj.user_id)
        return {
            "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }

    def get_event(self, obj):
        if not obj.event_id:
            return
        event = Event.objects.get(id=obj.event_id)
        return {
            "id": event.user_id,
            "title": event.title,
        }

    def get_creator(self, obj):
        if not obj.creator_id:
            return
        user = User.objects.get(user_id=obj.creator_id)
        return {
            "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
