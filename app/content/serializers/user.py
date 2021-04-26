from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from dry_rest_permissions.generics import DRYGlobalPermissionsField

from app.content.models import Notification, Registration, Strike, User
from app.content.serializers.badge import BadgeSerializer
from app.content.serializers.event import EventListSerializer
from app.content.serializers.strike import StrikeSerializer


class DefaultUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "user_id",
            "first_name",
            "last_name",
            "image",
        )
        read_only_fields = (
            "user_id",
            "first_name",
            "last_name",
            "image",
        )


class UserSerializer(serializers.ModelSerializer):
    events = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()
    unread_notifications = serializers.SerializerMethodField()
    permissions = DRYGlobalPermissionsField(actions=["write", "read"])
    strikes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "user_id",
            "first_name",
            "last_name",
            "image",
            "email",
            "cell",
            "home_busstop",
            "gender",
            "user_class",
            "user_study",
            "allergy",
            "tool",
            "app_token",
            "is_TIHLDE_member",
            "events",
            "groups",
            "badges",
            "unread_notifications",
            "permissions",
            "strikes",
        )
        read_only_fields = ("user_id",)
        write_only_fields = ("app_token",)

    def get_events(self, obj):
        """ Lists all events user is to attend or has attended """
        registrations = Registration.objects.filter(user__user_id=obj.user_id).order_by(
            "event__start_date"
        )
        events = [
            registration.event
            for registration in registrations
            if not registration.event.expired
        ]
        return EventListSerializer(events, many=True).data

    def get_badges(self, obj):
        """ Lists all badges a user has accomplished """
        user_badges = obj.user_badges.order_by("-created_at")
        badges = [user_badge.badge for user_badge in user_badges]
        return BadgeSerializer(badges, many=True).data

    def get_groups(self, obj):
        """ Lists all groups a user is a member of """
        return [group.name for group in obj.groups.all()]

    def get_unread_notifications(self, obj):
        """ Counts all unread notifications and returns the count """
        return Notification.objects.filter(user=obj, read=False).count()

    def get_strikes(self, obj):
        """ Get all active strikes """
        active_strikes = [
            strike for strike in Strike.objects.filter(user=obj) if strike.active
        ]
        return StrikeSerializer(active_strikes, many=True).data


class UserMemberSerializer(UserSerializer):
    """Serializer for user update to prevent them from updating extra_kwargs fields"""

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields
        read_only_fields = (
            "user_id",
            "first_name",
            "last_name",
            "email",
            "is_TIHLDE_member",
        )


class UserAdminSerializer(serializers.ModelSerializer):
    """Serializer for admin update to prevent them from updating extra_kwargs fields"""

    class Meta:
        model = User
        fields = (
            "user_id",
            "first_name",
            "last_name",
            "is_TIHLDE_member",
        )
        read_only_fields = (
            "user_id",
            "first_name",
            "last_name",
        )


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating user """

    class Meta:
        model = User
        fields = (
            "user_id",
            "password",
            "first_name",
            "last_name",
            "email",
            "user_class",
            "user_study",
        )

    def create(self, validated_data):
        user = User.objects.create(
            user_id=validated_data["user_id"],
            password=make_password(validated_data["password"]),
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
            user_class=validated_data["user_class"],
            user_study=validated_data["user_study"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

    def validate_email(self, data):
        if "@ntnu.no" in data:
            raise ValidationError(
                "Vi kan ikke sende epost til @ntnu.no-adresser, bruk @stud.ntnu.no-adressen istedenfor."
            )
        return data


class UserInAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user_id", "email"]
