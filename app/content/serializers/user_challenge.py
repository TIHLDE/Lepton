from rest_framework import serializers

from ..models import Challenge, User, UserChallenge


class UserChallengeSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    challenge = serializers.SerializerMethodField()

    class Meta:
        model = UserChallenge
        fields = ["user", "challenge"]

    def get_user(self, obj):
        """ Gets the necessary info from user """
        user = User.objects.get(user_id=obj.user_id)
        return {
            "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

    def get_challenge(self, obj):
        """ Gets the necessary info from user """
        challenge = Challenge.objects.get(id=obj.challenge_id)
        return {"id": challenge.id, "title": challenge.title, "year": challenge.year}
