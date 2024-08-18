import csv
from collections import OrderedDict

from django.http.response import HttpResponse


class SubmissionsCsvWriter:
    field_names = [
        "first_name",
        "last_name",
        "full_name",
        "email",
        "study",
        "studyyear",
    ]

    def __init__(self, queryset=None):
        if queryset is None:
            queryset = []
        self.queryset = queryset

    def write_csv(self):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="export.csv"'
        result = []

        for submission in self.queryset:
            self.create_row(result, submission)

        self.write_rows(response, result)

        return response

    def create_row(self, result, submission):
        user = submission.user
        row = OrderedDict(
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=f"{user.first_name} {user.last_name}",
            email=user.email,
            study=user.study.group.name,
            studyyear=user.studyyear.group.name,
        )
        for answer in submission.answers.all().prefetch_related(
            "selected_options", "field"
        ):
            self.create_column(answer, row)

        result.append(row)

    def create_column(self, answer, content):
        answer_text = self.get_answer_text(answer)
        field_name = answer.field.title

        if field_name not in self.field_names:
            self.field_names.append(field_name)

        content[field_name] = answer_text

    def get_answer_text(self, answer):
        if answer.selected_options.exists():
            answer_text = map(
                lambda option: option.title, answer.selected_options.all()
            )
            return ", ".join(answer_text)

        return answer.answer_text

    def write_rows(self, response, result):
        writer = csv.DictWriter(response, fieldnames=self.field_names)
        writer.writeheader()
        writer.writerows(result)
