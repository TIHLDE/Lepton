from app.codex.exceptions import (
    CodexCourseEndRegistrationDateAfterStartDate,
    CodexCourseEndRegistrationDateBeforeStartRegistrationDate,
)


def validate_course_dates(data: dict):
    if data["end_registration_at"] > data["start_date"]:
        raise CodexCourseEndRegistrationDateAfterStartDate(
            "Påmeldingsslutt kan ikke være etter kursstart"
        )

    if data["end_registration_at"] < data["start_registration_at"]:
        raise CodexCourseEndRegistrationDateBeforeStartRegistrationDate(
            "Påmeldingsslutt kan ikke være før påmeldingsstart"
        )
