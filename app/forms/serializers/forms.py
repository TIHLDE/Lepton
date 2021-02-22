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
        """
        - field that are not included in the request data are removed from the form
        - field is updated when the field id is not included in the request data
        - new fields are added when the field id is not included in the request data

        - oppdater formet på vanlig måte
            - fjerne fields før dette
        -
        """

        validated_fields = validated_data.pop("fields")
        super().update(instance, validated_data)

        field_ids_to_keep = []

        for field_data in validated_fields:
            options_data = field_data.pop("options", None)

            if "id" in field_data:
                Field.objects.filter(id=field_data["id"]).update(**field_data)
                current_field = Field.objects.get(id=field_data["id"])
                field_ids_to_keep.append(field_data["id"])
            else:
                current_field = Field.objects.create(form=instance, **field_data)
                field_ids_to_keep.append(current_field.id)

            if options_data is not None:
                # slett options som ikke er med
                # legg til de som er med og ikke er koblet til feltet
                # oppdater de som er med og er koblet til feltet

                option_ids_to_keep = []

                for option_data in options_data:
                    if "id" in option_data:
                        Option.objects.filter(id=option_data["id"]).update(
                            **option_data
                        )
                        option_ids_to_keep.append(option_data["id"])
                    else:
                        current_option = Option.objects.create(
                            field=current_field, **option_data
                        )
                        option_ids_to_keep.append(current_option.id)

                existing_options_ids = current_field.options.values_list(
                    "id", flat=True
                )
                option_ids_to_delete = set(existing_options_ids) - set(
                    option_ids_to_keep
                )
                for id_ in option_ids_to_delete:
                    Option.objects.get(id=id_).delete()

        existing_fields_ids = instance.fields.values_list("id", flat=True)
        field_ids_to_delete = set(existing_fields_ids) - set(field_ids_to_keep)

        for id_ in field_ids_to_delete:
            Field.objects.get(id=id_).delete()

        # legg til eller oppdater felter som er med
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
