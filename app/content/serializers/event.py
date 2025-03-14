from rest_framework import serializers

from dry_rest_permissions.generics import DRYPermissionsField
from sentry_sdk import capture_exception

from app.common.enums import NativeGroupType as GroupType
from app.common.serializers import BaseModelSerializer
from app.content.models import Event, PriorityPool
from app.content.serializers.category import SimpleCategorySerializer
from app.content.serializers.priority_pool import (
    PriorityPoolCreateSerializer,
    PriorityPoolSerializer,
)
from app.content.serializers.user import DefaultUserSerializer
from app.emoji.serializers.reaction import ReactionSerializer
from app.group.models.group import Group
from app.group.serializers.group import SimpleGroupSerializer
from app.payment.enums import OrderStatus
from app.payment.models.paid_event import PaidEvent
from app.payment.serializers.paid_event import PaidEventCreateSerializer


class EventSerializer(serializers.ModelSerializer):
    expired = serializers.BooleanField(read_only=True)
    priority_pools = PriorityPoolSerializer(many=True, read_only=True, required=False)
    evaluation = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    survey = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    organizer = SimpleGroupSerializer(read_only=True)
    permissions = DRYPermissionsField(
        actions=["write", "read"], object_only=True, read_only=True
    )
    paid_information = serializers.SerializerMethodField(
        required=False, allow_null=True
    )
    contact_person = DefaultUserSerializer(read_only=True, required=False)
    reactions = ReactionSerializer(read_only=True, many=True)
    category = SimpleCategorySerializer(read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "start_date",
            "end_date",
            "location",
            "description",
            "sign_up",
            "category",
            "expired",
            "limit",
            "closed",
            "list_count",
            "waiting_list_count",
            "organizer",
            "image",
            "image_alt",
            "start_registration_at",
            "end_registration_at",
            "sign_off_deadline",
            "only_allow_prioritized",
            "evaluation",
            "survey",
            "updated_at",
            "can_cause_strikes",
            "enforces_previous_strikes",
            "permissions",
            "priority_pools",
            "paid_information",
            "is_paid_event",
            "contact_person",
            "reactions",
            "emojis_allowed",
        )

    def get_paid_information(self, obj):
        if not obj.is_paid_event:
            return None

        paid_event = PaidEvent.objects.get(event=obj)
        if paid_event:
            return PaidEventCreateSerializer(paid_event).data
        return None

    def validate_limit(self, limit):
        """
        Validate that the event limit is greater or equal to 0 and
        that the limit can not be lower than the number of registered users.
        If the limit is already 0, then do not let that effect updating other fields
        """
        try:
            if limit < 0:
                raise serializers.ValidationError(
                    "Event limit can not a negative integer"
                )
            elif (
                limit < self.instance.registered_users_list.all().count()
                and self.instance.limit != 0
            ):
                raise serializers.ValidationError(
                    "Event limit can not be lower than number of registered users."
                )
        except AttributeError as attribute_error:
            capture_exception(attribute_error)

        return limit


class EventListSerializer(serializers.ModelSerializer):
    expired = serializers.BooleanField(read_only=True)
    organizer = SimpleGroupSerializer(read_only=True)
    category = SimpleCategorySerializer(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "start_date",
            "end_date",
            "location",
            "category",
            "expired",
            "organizer",
            "closed",
            "image",
            "image_alt",
            "updated_at",
        ]


class EventCreateAndUpdateSerializer(BaseModelSerializer):
    priority_pools = PriorityPoolCreateSerializer(many=True, required=False)
    paid_information = PaidEventCreateSerializer(required=False)

    class Meta:
        model = Event
        fields = (
            "can_cause_strikes",
            "category",
            "closed",
            "description",
            "end_date",
            "end_registration_at",
            "enforces_previous_strikes",
            "expired",
            "organizer",
            "image",
            "image_alt",
            "limit",
            "location",
            "only_allow_prioritized",
            "sign_off_deadline",
            "sign_up",
            "start_date",
            "start_registration_at",
            "title",
            "priority_pools",
            "paid_information",
            "is_paid_event",
            "contact_person",
            "emojis_allowed",
        )

    def to_internal_value(self, data):
        data.setdefault("paid_information", {})
        return super().to_internal_value(data)

    def create(self, validated_data):
        priority_pools_data = validated_data.pop("priority_pools", [])
        paid_information_data = validated_data.pop("paid_information", None)
        event = super().create(validated_data)
        self.set_priority_pools(event, priority_pools_data)

        if len(paid_information_data):
            self.set_paid_information(event, paid_information_data)

        return event

    def update(self, instance, validated_data):
        priority_pools_data = validated_data.pop("priority_pools", None)
        paid_information_data = validated_data.pop("paid_information", None)
        limit = validated_data.get("limit")
        instance_limit = instance.limit

        event = super().update(instance, validated_data)

        self.update_queue(event, limit, instance_limit)

        self.update_from_free_to_paid(event, paid_information_data)

        self.update_from_paid_to_free(event, paid_information_data)

        if len(paid_information_data):
            self.update_paid_information(event, paid_information_data)

        if priority_pools_data:
            self.update_priority_pools(event, priority_pools_data)

        event.save()
        return event

    def update_queue(self, event, limit, instance_limit):
        if not limit:
            return

        limit_difference = limit - instance_limit

        if limit_difference > 0 and event.waiting_list_count > 0:
            event.move_users_from_waiting_list_to_queue(limit_difference)

        if limit_difference < 0:
            event.move_users_from_queue_to_waiting_list(abs(limit_difference))

    def update_from_free_to_paid(self, event, paid_information_data):
        if paid_information_data and not event.is_paid_event:
            if event.has_participants:
                return

            PaidEvent.objects.create(
                event=event,
                price=paid_information_data["price"],
                paytime=paid_information_data["paytime"],
            )

    def update_from_paid_to_free(self, event, paid_information_data):
        if event.is_paid_event:
            if event.has_participants:
                return

            if not len(paid_information_data):
                paid_event = PaidEvent.objects.filter(event=event)
                if paid_event:
                    paid_event.first().delete()
                    event.paid_information = None

    def update_priority_pools(self, event, priority_pools_data):
        event.priority_pools.all().delete()
        self.set_priority_pools(event, priority_pools_data)

    def update_paid_information(self, event, paid_information_data):
        event.paid_information.price = paid_information_data["price"]
        event.paid_information.paytime = paid_information_data["paytime"]
        event.paid_information.save()

    @staticmethod
    def set_priority_pools(event, priority_pool_data):
        for priority_pool in priority_pool_data:
            groups = priority_pool.get("groups")
            priority_pool = PriorityPool.objects.create(event=event)
            priority_pool.groups.add(*groups)

    @staticmethod
    def set_paid_information(event, paid_information_data):
        price = paid_information_data.get("price")
        paytime = paid_information_data.get("paytime")
        paid_information = PaidEvent.objects.create(
            event=event, price=price, paytime=paytime
        )
        paid_information.save()


class EventStatisticsSerializer(BaseModelSerializer):
    has_attended_count = serializers.SerializerMethodField()
    studyyears = serializers.SerializerMethodField()
    studies = serializers.SerializerMethodField()
    has_allergy_count = serializers.SerializerMethodField()
    has_not_paid_count = serializers.SerializerMethodField()
    allow_photo_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            "has_attended_count",
            "list_count",
            "waiting_list_count",
            "studyyears",
            "studies",
            "has_allergy_count",
            "has_not_paid_count",
            "allow_photo_count",
        )

    def get_has_attended_count(self, obj, *_args, **_kwargs):
        return obj.registrations.filter(is_on_wait=False, has_attended=True).count()

    def get_has_allergy_count(self, obj, *args, **kwargs):
        return (
            obj.registrations.exclude(user__allergy__isnull=True)
            .filter(is_on_wait=False)
            .exclude(user__allergy__exact="")
            .count()
        )

    def get_studyyears(self, obj, *args, **kwargs):
        return filter(
            lambda studyyear: studyyear["amount"] > 0,
            map(
                lambda group: {
                    "studyyear": group.name,
                    "amount": obj.registrations.filter(
                        user__memberships__group=group, is_on_wait=False
                    ).count(),
                },
                Group.objects.filter(type=GroupType.STUDYYEAR),
            ),
        )

    def get_studies(self, obj, *_args, **_kwargs):
        return filter(
            lambda study: study["amount"] > 0,
            map(
                lambda group: {
                    "study": group.name,
                    "amount": obj.registrations.filter(
                        user__memberships__group=group, is_on_wait=False
                    ).count(),
                },
                Group.objects.filter(type=GroupType.STUDY),
            ),
        )

    def get_allow_photo_count(self, obj, *args, **kwargs):
        return obj.registrations.filter(allow_photo=False, is_on_wait=False).count()

    def get_has_not_paid_count(self, obj, *args, **kwargs):
        if obj.is_paid_event:
            registrations = obj.registrations.filter(is_on_wait=False).count()
            orders = obj.orders.filter(status=OrderStatus.SALE, event=obj).count()
            return registrations - orders
        return 0
