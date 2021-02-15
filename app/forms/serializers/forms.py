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
        form = self.Meta.model.objects.create(**validated_data)

        if fields:
            form.add_fields(fields)

        return form


    def update(self, instance, validated_data):
        """
        - field that are not included in the request data are removed from the form
        - field is updated when the field id is not included in the request data
        - new fields are added when the field id is not included in the request data

        - oppdater formet på vanlig måte
            - fjerne fields før dette
        -
        """
        print(instance)
        print(validated_data)

        fields = validated_data.pop("fields")
        super().update(instance, validated_data)

        # slette fields som ikke er med
        ids_to_update = []
        for field in fields:
            if "id" in field:
                ids_to_update.append(field["id"])

        existing_fields_ids = instance.fields.values_list("id", flat=True)

        ids_to_delete = set(existing_fields_ids) - set(ids_to_update)
        for id_ in ids_to_delete:
            Field.objects.get(id=id_).delete()

        # legg til eller oppdater felter som er med


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
