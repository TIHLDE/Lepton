from app.celery import app
from app.content.models.registration import Registration
from app.payment.models.order import Order
from app.payment.enums import OrderStatus
from app.util.tasks import BaseTask

@app.task(bind=True, base=BaseTask)
def check_if_has_paid(order_id, registration_id):
    try:
        order = Order.objects.get(order_id=order_id)
        order_status = order.status

        if order_status is not OrderStatus.CAPTURE or order_status is not OrderStatus.RESERVE:
            Registration.objects.filter(registration_id=registration_id).delete()

    except Exception as e:
        print(e)

    
