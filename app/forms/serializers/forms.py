from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from rest_polymorphic.serializers import PolymorphicSerializer

from app.common.serializers import BaseModelSerializer
from app.forms.models import EventForm, Field, Form, Option
from app.forms.models.forms import Answer


class OptionSerializer(BaseModelSerializer):
    id = serializers.UUIDField(read_only=False, required=False)

    class Meta:
        model = Option
        fields = (
            "id",
            "title",
        )


class FieldSerializer(BaseModelSerializer):
    options = OptionSerializer(many=True, required=False, allow_null=True)
    id = serializers.UUIDField(read_only=False, required=False)

    class Meta:
        model = Field
        fields = (
            "id",
            "title",
            "options",
            "type",
            "required",
        )


class FormSerializer(BaseModelSerializer):
    fields = FieldSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Form
        fields = (
            "id",
            "title",
            "fields",
        )

    @atomic
    def create(self, validated_data):
        fields = validated_data.pop("fields", None)
        form = self.Meta.model.objects.create(**validated_data)

        if fields:
            form.add_fields(fields)

        return form

    @staticmethod
    def update_field_options(field, options):
        """Creates new options from data without `id` attached, updates options with `id` attached and removes unreferenced options."""
        updated_ids = list()
        created = list()

        for option in options:
            id = option.get("id")
            if id:
                Option.objects.filter(id=id).update(**option)
                updated_ids.append(id)
            else:
                created.append(option)

        options_to_delete = field.options.exclude(id__in=updated_ids)
        options_to_delete.delete()

        Option.objects.bulk_create(
            [Option(field=field, **option) for option in created]
        )

    @atomic
    def update(self, instance, validated_data):
        validated_fields = validated_data.pop("fields")
        super().update(instance, validated_data)

        field_ids_to_keep = list()

        for field_data in validated_fields:
            options_data = field_data.pop("options", None)
            field_id = field_data.get("id")

            if field_id:
                field_query = Field.objects.filter(id=field_id)
                field_query.update(**field_data)
                field_instance = field_query[0]
            else:
                field_instance = Field.objects.create(form=instance, **field_data)
                field_id = field_instance.id

            field_ids_to_keep.append(field_id)

            self.update_field_options(field_instance, options_data)

        fields_to_delete = instance.fields.exclude(id__in=field_ids_to_keep)
        fields_to_delete.delete()

        return instance


class EventFormSerializer(FormSerializer):
    class Meta:
        model = EventForm
        fields = (
            "id",
            "title",
            "event",
            "fields",
            "type",
        )


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
    }

    class Meta:
        model = Form
        fields = ("resource_type",) + FormSerializer.Meta.fields
