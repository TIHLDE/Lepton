from django.db.transaction import atomic
from rest_framework import serializers

from rest_polymorphic.serializers import PolymorphicSerializer

from app.common.mixins import OrderedModelSerializerMixin
from app.common.serializers import BaseModelSerializer
from app.content.serializers import EventListSerializer
from app.forms.models import EventForm, Field, Form, Option
from app.forms.models.forms import GroupForm
from app.group.serializers import GroupSerializer


class OptionSerializer(BaseModelSerializer):
    id = serializers.UUIDField(read_only=False, required=False)
    order = serializers.IntegerField(read_only=False, required=False)

    class Meta:
        model = Option
        fields = (
            "id",
            "title",
            "order",
        )


class FieldSerializer(BaseModelSerializer):
    options = OptionSerializer(many=True, required=False, allow_null=True)
    id = serializers.UUIDField(read_only=False, required=False)
    order = serializers.IntegerField(read_only=False, required=False)

    class Meta:
        model = Field
        fields = (
            "id",
            "title",
            "options",
            "type",
            "required",
            "order",
        )


class FormSerializer(BaseModelSerializer):
    fields = FieldSerializer(many=True, required=False, allow_null=True)
    resource_type = serializers.SerializerMethodField()
    viewer_has_answered = serializers.SerializerMethodField()

    class Meta:
        model = Form
        fields = (
            "id",
            "title",
            "fields",
            "template",
            "resource_type",
            "viewer_has_answered",
        )

    def get_resource_type(self, instance):
        return instance._meta.object_name

    def get_viewer_has_answered(self, obj):
        request = self.context.get("request", None)
        if request and request.user:
            return obj.submissions.filter(user=request.user).exists()
        return False

    @atomic
    def create(self, validated_data):
        fields = validated_data.pop("fields", None)
        form = self.Meta.model.objects.create(**validated_data)

        if fields:
            form.add_fields(fields)

        return form

    @atomic
    def update(self, instance, validated_data):
        validated_fields = validated_data.pop("fields", None)
        super().update(instance, validated_data)

        # Must explicitly check if is None, because "[]" evaluates to falsy but should be looped
        if validated_fields is None:
            return instance

        field_ids_to_keep = list()

        for field_data in validated_fields:
            options_data = field_data.pop("options", None)
            field_id = field_data.get("id")

            if field_id:
                field_query = Field.objects.filter(id=field_id)
                field_query.update(**field_data)
                field_instance = field_query[0]
                OrderedModelSerializerMixin.do_update_order(field_instance, field_data)
            else:
                field_instance = Field.objects.create(form=instance, **field_data)
                field_id = field_instance.id

            OrderedModelSerializerMixin.do_update_order(field_instance, field_data)

            field_ids_to_keep.append(field_id)

            self.update_field_options(field_instance, options_data)

        fields_to_delete = instance.fields.exclude(id__in=field_ids_to_keep)
        fields_to_delete.delete()

        return instance

    @staticmethod
    def update_field_options(field, options):
        """Creates new options from data without `id` attached, updates options with `id` attached and removes unreferenced options."""
        updated_ids = list()
        created = list()

        for option in options:
            option_id = option.get("id")
            if option_id:
                options_query = Option.objects.filter(id=option_id)
                options_query.update(**option)
                option_instance = options_query.first()
                updated_ids.append(option_id)
                OrderedModelSerializerMixin.do_update_order(option_instance, option)
            else:
                created.append(option)

        options_to_delete = field.options.exclude(id__in=updated_ids)
        options_to_delete.delete()

        Option.objects.bulk_create(
            [Option(field=field, **option) for option in created]
        )


class EventFormSerializer(FormSerializer):
    class Meta:
        model = EventForm
        fields = FormSerializer.Meta.fields + ("event", "type",)

    def to_representation(self, instance):
        self.fields["event"] = EventListSerializer(read_only=True)
        return super(EventFormSerializer, self).to_representation(instance)


class GroupFormSerializer(FormSerializer):
    class Meta:
        model = GroupForm
        fields = FormSerializer.Meta.fields + (
            "group",
            "can_submit_multiple",
            "is_open_for_submissions",
            "only_for_group_members",
            "email_receiver_on_submit",
        )

    def to_representation(self, instance):
        self.fields["group"] = GroupSerializer(read_only=True)
        return super().to_representation(instance)


class FormInSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = ("id", "type")


class FieldInAnswerSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=False, required=True)

    class Meta:
        model = Field
        fields = ("id",)


class FormPolymorphicSerializer(PolymorphicSerializer, serializers.ModelSerializer):
    resource_type = serializers.CharField()
    resource_type_field_name = "resource_type"

    model_serializer_mapping = {
        Form: FormSerializer,
        EventForm: EventFormSerializer,
        GroupForm: GroupFormSerializer,
    }

    class Meta:
        model = Form
        fields = FormSerializer.Meta.fields
