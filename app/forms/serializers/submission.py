from rest_framework import serializers
from rest_framework.exceptions import MethodNotAllowed

from app.common.serializers import BaseModelSerializer
from app.forms.models import Answer, Field, Option, Submission
from app.forms.serializers import FieldInAnswerSerializer, OptionSerializer


class AnswerSerializer(serializers.ModelSerializer):
    field = FieldInAnswerSerializer()
    selected_options = OptionSerializer(many=True, required=False)

    class Meta:
        model = Answer
        fields = ["id", "field", "selected_options", "answer_text"]

    def validate(self, data):
        if "selected_options" in data and "answer_text" in data:
            raise serializers.ValidationError(
                "Du kan ikke svare med både alternativer og tekst på samme spørsmål."
            )
        return data


class BaseSubmissionSerializer(BaseModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Submission
        fields = ("answers",)


class SubmissionSerializer(BaseSubmissionSerializer):
    from app.content.serializers.user import UserInAnswerSerializer

    user = UserInAnswerSerializer(read_only=True)

    class Meta:
        model = BaseSubmissionSerializer.Meta.model
        fields = BaseSubmissionSerializer.Meta.fields + ("user",)

    def __create_answer_for_submission(self, submission, answer_data):
        field_id = answer_data.pop("field").get("id")
        selected_options_data = answer_data.pop("selected_options", None)

        answer = Answer.objects.create(
            submission=submission, field=Field.objects.get(id=field_id), **answer_data
        )

        if selected_options_data:
            selected_options_ids = [
                option.get("id") for option in selected_options_data
            ]
            selected_options = Option.objects.filter(id__in=selected_options_ids)
            answer.selected_options.set(selected_options)

        return answer

    def __create_submission(self, user, form_id, answers_data):
        submission = Submission.objects.create(user=user, form_id=form_id)

        for answer_data in answers_data:
            self.__create_answer_for_submission(submission, answer_data)

        return submission

    def create(self, validated_data):
        form_id = self.context.get("form_id")
        user = self.context.get("user")
        answers_data = validated_data.pop("answers")

        return self.__create_submission(user, form_id, answers_data)

    def update(self, **validated_data):
        raise MethodNotAllowed()


class SubmissionInRegistrationSerializer(BaseSubmissionSerializer):
    class Meta:
        model = BaseSubmissionSerializer.Meta.model
        fields = BaseSubmissionSerializer.Meta.fields + ("form",)
