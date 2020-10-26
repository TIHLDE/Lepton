from rest_framework import serializers

from app.forms.models import Form, Field, EventForm, Answer, Submission, Option
from app.content.serializers import EventInFormSerializer


class FormSerializer(serializers.ModelSerializer):
    fields = Form

    class Meta:
        model = Form
        fields = [
            "id",
            "title",
            "fields"
        ]


class FieldSerializer(serializers.ModelSerializer):
    fields = Field
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


class EventFormSerializer(FormSerializer):
    fields = EventForm
    event = EventInFormSerializer()
    field = FieldSerializer()

    class Meta:
        model = EventForm
        fields = [
            "id",
            "title",
            "event",
            "field",
        ]
