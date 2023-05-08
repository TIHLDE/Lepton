from app.celery import app
from app.content.models.registration import Registration
from app.payment.enums import OrderStatus
from app.payment.models.order import Order
from app.payment.views.vipps_callback import vipps_callback
from app.util.tasks import BaseTask


@app.task(bind=True, base=BaseTask)
def check_if_has_paid(self, order_id, registration_id):
    try:
        vipps_callback(None, order_id)
        order = Order.objects.get(order_id=order_id)
        order_status = order.status
        if (
            order_status != OrderStatus.CAPTURE
            and order_status != OrderStatus.RESERVE
            and order_status != OrderStatus.SALE
        ):
            Registration.objects.filter(registration_id=registration_id).delete()

    except Exception as e:
        print(e)
