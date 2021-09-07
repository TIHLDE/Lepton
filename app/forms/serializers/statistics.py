from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from rest_polymorphic.serializers import PolymorphicSerializer

from app.common.serializers import BaseModelSerializer
from app.forms.models import EventForm, Field, Form, Option
from app.forms.models.forms import Answer


class OptionStatisticsSerializer(BaseModelSerializer):
    id = serializers.UUIDField(read_only=False, required=False)
    answer_amount = SerializerMethodField(required=False)

    class Meta:
        model = Option
        fields = ("id", "title", "answer_amount")

    def get_answer_amount(self, obj):
        return Answer.objects.filter(selected_options=obj).count()


class FieldStatisticsSerializer(BaseModelSerializer):
    options = OptionStatisticsSerializer(many=True, required=False, allow_null=True)
    id = serializers.UUIDField(read_only=False, required=False)

    class Meta:
        model = Field
        fields = ("id", "title", "options", "type", "required")



class FormStatisticsSerializer(BaseModelSerializer):
    statistics = FieldStatisticsSerializer(
        many=True, required=False, allow_null=True, source="fields", 
    )

    class Meta:
        model = Form
        fields = (
            "id",
            "title",
            "statistics",
        )


class EventStatisticsFormSerializer(FormStatisticsSerializer):
    class Meta:
        model = EventForm
        fields = FormStatisticsSerializer.Meta.fields + ("event", "type")


class FormStatisticsSerializer(PolymorphicSerializer, serializers.ModelSerializer):
    resource_type = serializers.CharField()
    resource_type_field_name = "resource_type"

    model_serializer_mapping = {
        Form: FormStatisticsSerializer,
        EventForm: EventStatisticsFormSerializer,
    }

    class Meta:
        model = Form
        fields = ("resource_type",) + FormStatisticsSerializer.Meta.fields
