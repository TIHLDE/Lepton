from sentry_sdk import capture_exception

from app.celery import app
from app.content.models.event import Event
from app.content.models.registration import Registration
from app.payment.models.order import Order
from app.payment.util.order_utils import check_if_order_is_paid
from app.payment.views.vipps_callback import vipps_callback
from app.util.tasks import BaseTask


@app.task(bind=True, base=BaseTask)
def check_if_has_paid(self, event_id, registration_id):
    registration = Registration.objects.filter(registration_id=registration_id).first()
    event = Event.objects.filter(id=event_id).first()

    if not registration or not event:
        return

    user_order = Order.objects.filter(event=event, user=registration.user).first()

    if not user_order:
        registration.delete()
        return

    order = vipps_callback(None, user_order.order_id)

    if not check_if_order_is_paid(order):
        registration.delete()
