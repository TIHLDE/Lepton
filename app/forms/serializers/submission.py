from app.common.serializers import BaseModelSerializer
from app.content.serializers import UserInAnswerSerializer
from app.forms.models import Answer, Submission
from app.forms.serializers import (
    FieldInAnswerSerializer,
    FormInSubmissionSerializer,
    OptionSerializer,
)


class AnswerSerializer(BaseModelSerializer):
    field = FieldInAnswerSerializer(read_only=True)
    selected_options = OptionSerializer(read_only=True)

    class Meta:
        model = Answer
        fields = ["id", "field", "selected_options", "answer_text"]


class SubmissionSerializer(BaseModelSerializer):
    user = UserInAnswerSerializer(read_only=True)
    answer = AnswerSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = ["user", "answers"]
