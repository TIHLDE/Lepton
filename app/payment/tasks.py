from app.celery import app
from app.content.models.event import Event
from app.content.models.registration import Registration
from app.payment.enums import OrderStatus
from app.payment.models.order import Order
from app.payment.util.order_utils import has_paid_order
from app.payment.views.vipps_callback import vipps_callback
from app.util.tasks import BaseTask


@app.task(bind=True, base=BaseTask)
def check_if_has_paid(self, event_id, registration_id):
    registration = Registration.objects.filter(registration_id=registration_id).first()
    event = Event.objects.filter(id=event_id).first()

    if not registration or not event:
        return

    user_orders = Order.objects.filter(event=event, user=registration.user)

    if not user_orders:
        registration.delete()
        return

    if not has_paid_order(user_orders):
        registration.delete()
