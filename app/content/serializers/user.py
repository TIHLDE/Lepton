from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from dry_rest_permissions.generics import DRYGlobalPermissionsField

from app.common.enums import GroupType
from app.common.serializers import BaseModelSerializer
from app.content.models import User
from app.group.models import Group, Membership


class DefaultUserSerializer(BaseModelSerializer):
    study = serializers.SerializerMethodField()
    studyyear = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "user_id",
            "first_name",
            "last_name",
            "image",
            "email",
            "gender",
            "study",
            "studyyear",
        )
        read_only_fields = (
            "user_id",
            "first_name",
            "last_name",
            "image",
            "email",
            "gender",
            "study",
            "studyyear",
        )

    def get_study(self, obj):
        from app.group.serializers.membership import BaseMembershipSerializer

        return BaseMembershipSerializer(obj.study).data

    def get_studyyear(self, obj):
        from app.group.serializers.membership import BaseMembershipSerializer

        return BaseMembershipSerializer(obj.studyyear).data


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
            "slack_user_id",
            "allows_photo_by_default",
            "accepts_event_rules",
        )
        read_only_fields = ("user_id",)

    def get_unread_notifications(self, obj):
        """Counts all unread notifications and returns the count"""
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
            "allergy",
            "tool",
            "number_of_strikes",
            "study",
            "studyyear",
        )


class UserMemberSerializer(UserSerializer):
    """Serializer for user update to prevent them from updating extra_kwargs fields"""

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields
        read_only_fields = UserSerializer.Meta.read_only_fields + (
            "first_name",
            "last_name",
            "email",
        )


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "user_id",
            "first_name",
            "last_name",
        )


class UserCreateSerializer(serializers.ModelSerializer):
    study = serializers.SlugRelatedField(
        slug_field="slug",
        allow_null=True,
        queryset=Group.objects.filter(type=GroupType.STUDY),
    )
    class_ = serializers.SlugRelatedField(
        slug_field="slug",
        allow_null=True,
        queryset=Group.objects.filter(type=GroupType.STUDYYEAR),
    )

    class Meta:
        model = User
        fields = (
            "user_id",
            "password",
            "first_name",
            "last_name",
            "email",
            "study",
            "class_",
        )

    def create(self, validated_data):
        study = validated_data.pop("study", None)
        class_ = validated_data.pop("class", None)

        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data["password"])
        user.save()

        if study and class_:
            self.add_user_to_class_and_study(user, study, class_)

        return user

    @staticmethod
    def add_user_to_class_and_study(user, study, class_):
        Membership.objects.create(user=user, group=study)
        Membership.objects.create(user=user, group=class_)

    def validate_email(self, data):
        if "@ntnu.no" in data:
            raise ValidationError(
                "Vi kan ikke sende epost til @ntnu.no-adresser, bruk @stud.ntnu.no-adressen istedenfor."
            )
        return data

    def get_fields(self):
        """'class' is a reserved keyword in python resulting in the field being named 'class_'. This enables us to use 'class' in the request and 'class_' in the code."""
        result = super().get_fields()
        # Rename `class_` to `class`
        class_ = result.pop("class_")
        result["class"] = class_
        return result


class UserPermissionsSerializer(serializers.ModelSerializer):
    permissions = DRYGlobalPermissionsField(
        actions=[
            "write",
            "write_all",
            "read",
            "destroy",
            "update",
            "retrieve",
            "get_user_detail_strikes",
        ]
    )

    class Meta:
        model = User
        fields = ("permissions",)
