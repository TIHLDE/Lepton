from rest_framework import serializers

from app.content.serializers import UserInAnswerSerializer
from app.forms.models import Answer, Submission
from app.forms.serializers import (
    FieldInAnswerSerializer,
    FormInSubmissionSerializer,
    OptionSerializer,
)


class AnswerSerializer(serializers.ModelSerializer):
    field = FieldInAnswerSerializer(read_only=True)
    selected_options = OptionSerializer(read_only=True)

    class Meta:
        model = Answer
        fields = ["id", "field", "selected_options", "answer_text"]


class SubmissionSerializer(serializers.ModelSerializer):
    form = FormInSubmissionSerializer(read_only=True)
    user = UserInAnswerSerializer(read_only=True)
    answer = AnswerSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = ["form", "user", "answers"]
