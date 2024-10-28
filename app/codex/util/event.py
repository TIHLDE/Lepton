from app.codex.exceptions import (
    CodexEventEndRegistrationDateAfterStartDate,
    CodexEventEndRegistrationDateBeforeStartRegistrationDate,
)


def validate_event_dates(data: dict):
    if data["end_registration_at"] > data["start_date"]:
        raise CodexEventEndRegistrationDateAfterStartDate()

    if data["end_registration_at"] < data["start_registration_at"]:
        raise CodexEventEndRegistrationDateBeforeStartRegistrationDate()
