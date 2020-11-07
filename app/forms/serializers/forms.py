from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from app.forms.models import Form, Field, EventForm, Answer, Submission, Option
from app.content.serializers import EventInFormSerializer


class OptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = [
            "id",
            "title",
        ]


class FieldSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

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
    fields = FieldSerializer(many=True)

    class Meta:
        model = Form
        fields = [
            "id",
            "title",
            "fields",
        ]

    def create(self, validated_data):
        print(validated_data)
        form = Form.objects.create()
        return form


class EventFormSerializer(FormSerializer):
    event = EventInFormSerializer(read_only=True)

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
        fields = [
            "id",
            "type"
        ]


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

