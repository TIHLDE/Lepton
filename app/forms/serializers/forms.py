from rest_framework import serializers

from app.forms.models import Form, Field, EventForm, Answer, Submission, Option
from app.content.serializers import EventInFormSerializer

class FieldSerializer(serializers.ModelSerializer):
    options = Option

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
    fields = FieldSerializer()

    class Meta:
        model = Form
        fields = [
            "id",
            "title",
            "fields"
        ]


class OptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = [
            "id",
            "title",
            "field"
        ]

class EventFormSerializer(FormSerializer):
    event = EventInFormSerializer()

    class Meta:
        model = EventForm
        fields = [
            "id",
            "title",
            "event",
            "field",
        ]
