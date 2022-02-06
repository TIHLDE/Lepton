from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from dry_rest_permissions.generics import DRYGlobalPermissionsField

from app.common.serializers import BaseModelSerializer
from app.content.models import User


class DefaultUserSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = (
            "user_id",
            "first_name",
            "last_name",
            "image",
            "email",
            "gender",
            "user_class",
            "user_study",
        )
        read_only_fields = (
            "user_id",
            "first_name",
            "last_name",
            "image",
            "email",
            "gender",
            "user_class",
            "user_study",
        )


class UserSerializer(DefaultUserSerializer):
    unread_notifications = serializers.SerializerMethodField()
    unanswered_evaluations_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = DefaultUserSerializer.Meta.fields + (
            "allergy",
            "tool",
            "public_event_registrations",
            "unread_notifications",
            "unanswered_evaluations_count",
            "number_of_strikes",
        )
        read_only_fields = ("user_id",)

    def get_unread_notifications(self, obj):
        """ Counts all unread notifications and returns the count """
        return obj.notifications.filter(read=False).count()

    def get_unanswered_evaluations_count(self, obj):
        return obj.get_unanswered_evaluations().count()


class UserListSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            "user_id",
            "first_name",
            "last_name",
            "image",
            "email",
            "gender",
            "user_class",
            "user_study",
            "allergy",
            "tool",
            "number_of_strikes",
        )


class UserMemberSerializer(UserSerializer):
    """Serializer for user update to prevent them from updating extra_kwargs fields"""

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields
        read_only_fields = UserSerializer.Meta.read_only_fields + (
            "first_name",
            "last_name",
            "email",
            "user_class",
            "user_study",
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


class UserPermissionsSerializer(serializers.ModelSerializer):
    permissions = DRYGlobalPermissionsField(actions=["write", "read", "destroy"])

    class Meta:
        model = User
        fields = ("permissions",)
