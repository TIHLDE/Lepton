import uuid


def is_valid_uuid(uuid_to_test) -> bool:
    """Check if the given string is a valid UUID."""
    try:
        uuid_obj = uuid.UUID(uuid_to_test)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test
