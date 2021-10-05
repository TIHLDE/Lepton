from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from dry_rest_permissions.generics import DRYGlobalPermissionsField

from app.content.models import Notification, User


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
    unread_notifications = serializers.SerializerMethodField()
    permissions = DRYGlobalPermissionsField(actions=["write", "read"])
    unanswered_evaluations_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "user_id",
            "first_name",
            "last_name",
            "image",
            "email",
            "cell",
            "gender",
            "user_class",
            "user_study",
            "allergy",
            "tool",
            "unread_notifications",
            "unanswered_evaluations_count",
            "permissions",
        )
        read_only_fields = ("user_id",)

    def get_unread_notifications(self, obj):
        """ Counts all unread notifications and returns the count """
        return Notification.objects.filter(user=obj, read=False).count()

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
            "cell",
            "gender",
            "user_class",
            "user_study",
            "allergy",
            "tool",
        )


class UserMemberSerializer(UserSerializer):
    """Serializer for user update to prevent them from updating extra_kwargs fields"""

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields
        read_only_fields = (
            "user_id",
            "first_name",
            "last_name",
            "email",
            "user_class",
            "user_study",
        )


class UserAdminSerializer(serializers.ModelSerializer):
    """Serializer for admin update to prevent them from updating extra_kwargs fields"""

    class Meta(UserListSerializer.Meta):
        fields = UserListSerializer.Meta.fields
        read_only_fields = (
            "user_id",
            "strikes",
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
