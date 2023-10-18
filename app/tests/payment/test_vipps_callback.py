API_EVENT_BASE_URL = "/events/"


def _get_registration_url(event):
    return f"{API_EVENT_BASE_URL}{event.pk}/registrations/"


def _get_registration_post_data(user, event):
    return {
        "user_id": user.user_id,
        "event": event.pk,
    }
