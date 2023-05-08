API_EVENT_BASE_URL = "/events/"
API_PAYMENT_BASE_URL = "/payment/"


def _get_registration_url(event):
    return f"{API_EVENT_BASE_URL}{event.pk}/registrations/"


def _get_order_url():
    return f"{API_PAYMENT_BASE_URL}order/"


def _get_registration_post_data(user, event):
    return {
        "user_id": user.user_id,
        "event": event.pk,
    }


def _get_order_data(user, event):
    return {"user_id": user.user_id, "event": event.pk}
