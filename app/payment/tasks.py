from app.celery import app
from app.content.models.registration import Registration
from app.payment.models.order import Order
from app.payment.enums import OrderStatus
from app.util.tasks import BaseTask

@app.task(bind=True, base=BaseTask)
def check_if_has_paid(self, order_id, registration_id):
    try:
        print(app.conf.task_always_eager)
        order = Order.objects.get(order_id=order_id)
        order_status = order.status
        if order_status != OrderStatus.CAPTURE and order_status != OrderStatus.RESERVE:
            Registration.objects.filter(registration_id=registration_id).delete()

    except Exception as e:
        print(e)

    
