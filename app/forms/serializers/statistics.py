from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from rest_polymorphic.serializers import PolymorphicSerializer

from app.common.serializers import BaseModelSerializer
from app.forms.enums import FormFieldType
from app.forms.models import EventForm, Field, Form, Option
from app.forms.models.forms import Answer


class OptionStatisticsSerializer(BaseModelSerializer):
    id = serializers.UUIDField(read_only=False, required=False)
    answer_amount = SerializerMethodField(required=False)
    answer_percentage = SerializerMethodField()

    class Meta:
        model = Option
        fields = ("id", "title", "answer_amount", "answer_percentage")

    def get_answer_amount(self, obj):
        return Answer.objects.filter(selected_options=obj).count()

    def get_answer_percentage(self, obj):
        amount = self.get_answer_amount(obj)
        total = obj.field.form.submissions.count()
        return round(amount / total * 100 if total > 0 else 0, 2)


class FieldStatisticsSerializer(BaseModelSerializer):
    options = OptionStatisticsSerializer(many=True, required=False, allow_null=True)
    id = serializers.UUIDField(read_only=False, required=False)

    class Meta:
        model = Field
        fields = ("id", "title", "options", "type", "required")


class FormStatisticsSerializer(BaseModelSerializer):
    statistics = SerializerMethodField()

    class Meta:
        model = Form
        fields = (
            "id",
            "title",
            "statistics",
        )

    def get_statistics(self, obj):
        fields = Field.objects.filter(form=obj).exclude(type=FormFieldType.TEXT_ANSWER)
        return FieldStatisticsSerializer(
            fields, many=True, required=False, allow_null=True
        ).data


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
