import pytest
from app.payment.factories.paid_event_factory import PaidEventFactory
from app.payment.enums import OrderStatus
from app.content.models.event import Event
from datetime import time
from app.payment.tasks import check_if_has_paid
from app.content.factories.registration_factory import RegistrationFactory
from app.payment.factories.order_factory import OrderFactory
from app.content.models.registration import Registration


@pytest.mark.django_db
def test_check_if_has_paid_task_registration_is_deleted():
    paid_event = PaidEventFactory(paytime=time(second=3))
    registration_initiate = RegistrationFactory(event=paid_event.event)
    registration_refund = RegistrationFactory(event=paid_event.event)
    order_initate = OrderFactory(status=OrderStatus.INITIATE, event=paid_event.event)
    order_refund = OrderFactory(status=OrderStatus.REFUND, event=paid_event.event)
    paytime = Event.objects.all()[0].paid_information.paytime

    assert len(Registration.objects.all())

    check_if_has_paid.apply_async(args=(order_initate.order_id, registration_initiate.registration_id), timeout=paytime)
    check_if_has_paid.apply_async(args=(order_refund.order_id, registration_refund.registration_id), timeout=paytime)

    assert len(Registration.objects.all()) == 0

@pytest.mark.django_db
def test_check_if_has_paid_task_registration_is_not_deleted():
    paid_event = PaidEventFactory(paytime=time(second=3))
    registration_capture = RegistrationFactory(event=paid_event.event)
    registration_reserve = RegistrationFactory(event=paid_event.event)
    order_capture = OrderFactory(status=OrderStatus.CAPTURE, event=paid_event.event)
    order_reserve = OrderFactory(status=OrderStatus.CAPTURE, event=paid_event.event)
    paytime = Event.objects.all()[0].paid_information.paytime

    assert len(Registration.objects.all()) == 2

    check_if_has_paid.apply_async(args=(order_capture.order_id, registration_capture.registration_id), timeout=paytime)
    check_if_has_paid.apply_async(args=(order_reserve.order_id, registration_reserve.registration_id), timeout=paytime)

    assert len(Registration.objects.all()) == 2