import pytest

from app.content.models.registration import Registration
from rest_framework import status
from app.payment.models.order import Order
from app.payment.factories.paid_event_factory import PaidEventFactory
from datetime import time
from time import sleep
from app.util.test_utils import get_api_client

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
    return {
        "user_id": user.user_id,
        "event": event.pk
    }
