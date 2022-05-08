from django.db.models.aggregates import Sum
from django.db.transaction import atomic
from rest_framework import serializers

from app.common.serializers import BaseModelSerializer
from app.content.models.user import User
from app.content.serializers.user import DefaultUserSerializer
from app.group.models.fine import Fine
from app.group.models.group import Group
from app.group.serializers.group import SimpleGroupSerializer


class FineListSerializer(serializers.ListSerializer):
    @atomic
    def create(self, validated_data):
        validated_data = validated_data[0]
        group = Group.objects.get(slug=self.context["group_slug"])
        users = User.objects.filter(user_id__in=self.context["user_ids"])
        created_by = User.objects.get(user_id=self.context["created_by"])

        fines = [
            Fine.objects.create(
                group=group, created_by=created_by, user=user, **validated_data
            )
            for user in users
        ]
        return fines

    @atomic
    def update(self, instance, validated_data):
        validated_data = self.context["data"]
        instance.update(**validated_data)

        return instance


class FineUpdateCreateSerializer(BaseModelSerializer):
    user = DefaultUserSerializer(read_only=True)
    group = SimpleGroupSerializer(read_only=True)

    class Meta:
        model = Fine
        list_serializer_class = FineListSerializer
        fields = (
            "id",
            "user",
            "group",
            "amount",
            "description",
            "created_at",
            "reason",
            "image",
        )

        read_only_fields = (
            "user",
            "group",
        )

    def create(self, validated_data):
        group = Group.objects.get(slug=self.context["group_slug"])
        user = User.objects.get(user_id=self.context["user_id"])
        created_by = User.objects.get(user_id=self.context["created_by"])
        return Fine.objects.create(
            group=group, created_by=created_by, user=user, **validated_data
        )


class FineUpdateDefenseSerializer(BaseModelSerializer):
    class Meta:
        model = Fine
        fields = ("defense",)


class FineSerializer(BaseModelSerializer):
    user = DefaultUserSerializer(read_only=True)
    created_by = DefaultUserSerializer(read_only=True)

    class Meta:
        model = Fine
        fields = (
            "id",
            "user",
            "amount",
            "approved",
            "payed",
            "description",
            "reason",
            "defense",
            "image",
            "created_by",
            "created_at",
        )

        read_only_fields = (
            "user",
            "created_by",
            "defense",
        )


class FineNoUserSerializer(BaseModelSerializer):
    created_by = DefaultUserSerializer(read_only=True)

    class Meta:
        model = Fine
        fields = (
            "id",
            "amount",
            "approved",
            "payed",
            "description",
            "reason",
            "defense",
            "image",
            "created_by",
            "created_at",
        )

        read_only_fields = (
            "created_by",
            "defense",
        )


class UserFineSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    fines_amount = serializers.IntegerField()

    class Meta:
        model = User
        fields = ("user", "fines_amount")

    def get_user(self, obj):
        return DefaultUserSerializer(obj).data


class FineStatisticsSerializer(BaseModelSerializer):

    payed = serializers.SerializerMethodField()
    approved_and_not_payed = serializers.SerializerMethodField()
    not_approved = serializers.SerializerMethodField()

    class Meta:
        model = Group

        fields = ("payed", "approved_and_not_payed", "not_approved")

    def get_sum(self, obj, *args, **kwargs):
        sum = obj.fines.filter(*args, **kwargs).aggregate(sum=Sum("amount"))["sum"]
        return sum if sum else 0

    def get_payed(self, obj):
        return self.get_sum(obj, payed=True)

    def get_approved_and_not_payed(self, obj):
        return self.get_sum(obj, payed=False, approved=True)

    def get_not_approved(self, obj):
        return self.get_sum(obj, approved=False)
