from app.codex.exceptions import (
    CodexCourseEndDateBeforeStartDate,
    CodexCourseEndRegistrationDateAfterStartDate,
    CodexCourseEndRegistrationDateBeforeStartRegistrationDate,
    CodexCourseSignOffDeadlineAfterStartDate,
)


def validate_course_dates(data: dict):
    if data["end_date"] < data["start_date"]:
        raise CodexCourseEndDateBeforeStartDate()

    if data["end_registration_at"] > data["start_date"]:
        raise CodexCourseEndRegistrationDateAfterStartDate()

    if data["end_registration_at"] < data["start_registration_at"]:
        raise CodexCourseEndRegistrationDateBeforeStartRegistrationDate()

    if data["sign_off_deadline"] > data["start_date"]:
        raise CodexCourseSignOffDeadlineAfterStartDate()
