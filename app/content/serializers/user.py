from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.contrib.auth.hashers import make_password

from dry_rest_permissions.generics import DRYGlobalPermissionsField

from app.common.enums import Groups, GroupType
from app.common.serializers import BaseModelSerializer
from app.communication.enums import UserNotificationSettingType
from app.communication.notifier import Notify
from app.content.exceptions import FeideUserExistsError
from app.content.models import User
from app.content.serializers.user_bio import UserBioSerializer
from app.content.util.feide_utils import (
    generate_random_password,
    get_feide_tokens,
    get_feide_user_groups,
    get_feide_user_info_from_jwt,
    get_study_year,
    parse_feide_groups,
)
from app.group.models import Group, Membership
from app.content.util.feide_utils import (
    get_feide_tokens,
    get_feide_user_groups,
    parse_feide_groups,
    generate_random_password,
    get_study_year,
    get_feide_user_info_from_jwt,
)
from app.content.exceptions import FeideUserExistsError


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
    bio = UserBioSerializer(read_only=True, required=False)

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
            "bio",
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


class FeideUserCreateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=36)

    def create(self, validated_data):
        code = validated_data["code"]

        access_token, jwt_token = get_feide_tokens(code)
        full_name, username = get_feide_user_info_from_jwt(jwt_token)

        existing_user = User.objects.filter(user_id=username).first()
        if existing_user:
            raise FeideUserExistsError()

        groups = get_feide_user_groups(access_token)
        group_slugs = parse_feide_groups(groups)
        password = generate_random_password()

        user_info = {
            "user_id": username,
            "password": make_password(password),
            "first_name": full_name.split()[0],
            "last_name": " ".join(full_name.split()[1:]),
            "email": f"{username}@stud.ntnu.no",
        }

        user = User.objects.create(**user_info)

        self.make_TIHLDE_member(user, password)

        for slug in group_slugs:
            self.add_user_to_study(user, slug)

        return user

    def add_user_to_study(self, user, slug):
        study = Group.objects.filter(type=GroupType.STUDY, slug=slug).first()
        study_year = get_study_year(slug)
        class_ = Group.objects.get_or_create(
            name=study_year, type=GroupType.STUDYYEAR, slug=study_year
        )

        if not study or not class_:
            return

        Membership.objects.create(user=user, group=study)
        Membership.objects.create(user=user, group=class_[0])

    def make_TIHLDE_member(self, user, password):
        TIHLDE = Group.objects.get(slug=Groups.TIHLDE)
        Membership.objects.get_or_create(user=user, group=TIHLDE)

        Notify(
            [user], "Velkommen til TIHLDE", UserNotificationSettingType.OTHER
        ).add_paragraph(f"Hei, {user.first_name}!").add_paragraph(
            f"Din bruker har nå blitt automatisk generert ved hjelp av Feide. Ditt brukernavn er dermed ditt brukernavn fra Feide: {user.user_id}. Du kan nå logge inn og ta i bruk våre sider."
        ).add_paragraph(
            f"Ditt autogenererte passord: {password}"
        ).add_paragraph(
            "Vi anbefaler at du bytter passord ved å følge lenken under:"
        ).add_link(
            "Bytt passord", "/glemt-passord/"
        ).add_link(
            "Logg inn", "/logg-inn/"
        ).send(
            website=False, slack=False
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
            "read_all",
            "destroy",
            "update",
            "retrieve",
        ]
    )

    class Meta:
        model = User
        fields = ("permissions",)
