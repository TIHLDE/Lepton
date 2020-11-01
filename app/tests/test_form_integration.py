import pytest


from rest_framework import status

import pytest

from app.content.enums import AdminGroup
from app.content.factories import EventFactory, RegistrationFactory
from app.util.test_utils import get_api_client


def _get_forms_url():
    return f"/api/v1/forms/"


def _get_form_detail_url(form):
    return f"{_get_forms_url()}{form.id}/"


def _get_form_post_data(form):
    return {
        "event": event.pk,
        "allow_photo": False,
    }


def _get_registration_put_data(user, event):
    return {
        **_get_registration_post_data(user, event),
        "is_on_wait": False,
        "has_attended": False,
    }
