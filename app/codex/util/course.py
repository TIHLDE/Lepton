from app.codex.exceptions import (
    CodexCourseEndRegistrationDateAfterStartDate,
    CodexCourseEndRegistrationDateBeforeStartRegistrationDate,
)


def validate_course_dates(data: dict):
    if data["end_registration_at"] > data["start_date"]:
        raise CodexCourseEndRegistrationDateAfterStartDate()

    if data["end_registration_at"] < data["start_registration_at"]:
        raise CodexCourseEndRegistrationDateBeforeStartRegistrationDate()
