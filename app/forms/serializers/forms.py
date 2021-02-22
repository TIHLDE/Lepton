from django.db.transaction import atomic
from rest_framework import serializers

from rest_polymorphic.serializers import PolymorphicSerializer

from app.forms.models import EventForm, Field, Form, Option


class OptionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=False, required=False)

    class Meta:
        model = Option
        fields = [
            "id",
            "title",
        ]


class FieldSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=False, allow_null=True)
    id = serializers.UUIDField(read_only=False, required=False)

    class Meta:
        model = Field
        fields = [
            "id",
            "title",
            "options",
            "type",
            "required",
        ]


class FormSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Form
        fields = [
            "id",
            "title",
            "fields",
        ]

    @atomic
    def create(self, validated_data):
        fields = validated_data.pop("fields", None)
        form = self.Meta.model.objects.create(**validated_data)

        if fields:
            form.add_fields(fields)

        return form

    @atomic
    def update(self, instance, validated_data):
        validated_fields = validated_data.pop("fields")
        super().update(instance, validated_data)

        updated_field_ids = list()
        fields_to_create = list()

        for field_data in validated_fields:
            options_data = field_data.pop("options", None)
            field_id = field_data.get("id")

            if field_id:
                Field.objects.filter(id=field_id).update(**field_data)
                field_instance = Field.objects.get(id=field_id)
                updated_field_ids.append(field_id)
            else:
                field_instance = Field.objects.create(form=instance, **field_data)
                fields_to_create.append(field_data)

            updated_options_id = list()
            options_to_create = list()

            for option_data in options_data:
                option_id = option_data.get("id")
                if option_id:
                    Option.objects.filter(id=option_id).update(**option_data)
                    updated_options_id.append(option_id)
                else:
                    options_to_create.append(option_data)

            options_to_delete = field_instance.options.exclude(
                id__in=updated_options_id
            )
            options_to_delete.delete()

            Option.objects.bulk_create(
                [Option(field=field_instance, **data) for data in options_to_create]
            )

        fields_to_delete = instance.fields.exclude(id__in=updated_field_ids)
        fields_to_delete.delete()

        Field.objects.bulk_create(
            [Field(form=instance, **data) for data in fields_to_create]
        )

        return instance


class EventFormSerializer(FormSerializer):
    class Meta:
        model = EventForm
        fields = [
            "id",
            "title",
            "event",
            "fields",
            "type",
        ]


class FormInSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = [
            "id",
            "type",
        ]


class FieldInAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ["id", "type"]


class FormPolymorphicSerializer(PolymorphicSerializer, serializers.ModelSerializer):
    resource_type = serializers.CharField()
    resource_type_field_name = "resource_type"

    model_serializer_mapping = {
        Form: FormSerializer,
        EventForm: EventFormSerializer,
    }

    class Meta:
        model = Form
        fields = ["resource_type"] + FormSerializer.Meta.fields
