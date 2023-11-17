from rest_framework import serializers

from app.blitzed.models.anonymous_user import AnonymousUser
from app.blitzed.models.pong_team import PongTeam
from app.blitzed.serializers.anonymous_user import AnonymousUserSerializer
from app.common.serializers import BaseModelSerializer


class PongTeamSerializer(BaseModelSerializer):
    anonymous_members = AnonymousUserSerializer(required=False, many=True)

    class Meta:
        model = PongTeam
        fields = ("id", "team_name", "members", "anonymous_members")


class SimplePongTeamSerializer(BaseModelSerializer):
    class Meta:
        model = PongTeam
        fields = ("id", "team_name")


class PongTeamCreateAndUpdateSerializer(serializers.ModelSerializer):
    anonymous_members = AnonymousUserSerializer(required=False, many=True)

    class Meta:
        model = PongTeam
        fields = ("id", "team_name", "members", "anonymous_members", "tournament")

    def _get_or_create_anonymous_users(self, team, anonymous_members):
        """Get or create anonymous users"""
        for member in anonymous_members:
            member, _ = AnonymousUser.objects.get_or_create(**member)
            team.anonymous_members.add(member)

    def create(self, validated_data):
        """Create a pong team"""
        anonymous_members = validated_data.pop("anonymous_members", [])
        members = validated_data.pop("members", [])
        team = PongTeam.objects.create(**validated_data)
        if members is not None:
            team.members.set(members)
        self._get_or_create_anonymous_users(team, anonymous_members)
        team.save()
        return team

    def update(self, instance, validated_data):
        """Update a pong team"""
        anonymous_members = validated_data.pop("anonymous_members", [])
        members = validated_data.pop("members", [])
        if anonymous_members is not None:
            instance.anonymous_members.clear()
            self._get_or_create_anonymous_users(instance, anonymous_members)
        if members is not None:
            instance.members.set(members)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
