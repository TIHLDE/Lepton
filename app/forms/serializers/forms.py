from rest_framework import serializers

from rest_polymorphic.serializers import PolymorphicSerializer

from app.forms.models import EventForm, Field, Form, Option


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = [
            "id",
            "title",
        ]


class FieldSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=False, allow_null=True)

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

    def create(self, validated_data):
        fields = validated_data.pop("fields", None)
        form = Form.objects.create(**validated_data)

        if fields:
            form.add_fields(fields)

        return form


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
