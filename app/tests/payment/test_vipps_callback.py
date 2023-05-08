API_EVENT_BASE_URL = "/events/"


def _get_registration_url(event):
    return f"{API_EVENT_BASE_URL}{event.pk}/registrations/"


def _get_registration_post_data(user, event):
    return {
        "user_id": user.user_id,
        "event": event.pk,
    }


# these tests can not be tested because of celery

# @pytest.mark.django_db
# def test_if_order_gets_updated_by_vipps_callback(member, paid_event):
#     """A member should be able to create a registration for themselves."""
#     data = _get_registration_post_data(member, paid_event)
#     client = get_api_client(user=member)

#     url = _get_registration_url(event=paid_event.event)
#     response = client.post(url, data=data)

#     assert response.status_code == status.HTTP_201_CREATED

#     order = Order.objects.all()[0]
#     order_id = order.order_id
#     order_status = order.status
#     new_status = vipps_callback({"orderId": order_id})

#     assert order_status == new_status

# @pytest.mark.django_db
# def test_force_vipps_payment(member, paid_event):
#     """A member should be able to create a registration for themselves."""
#     data = _get_registration_post_data(member, paid_event)
#     client = get_api_client(user=member)

#     url = _get_registration_url(event=paid_event.event)
#     response = client.post(url, data=data)

#     assert response.status_code == status.HTTP_201_CREATED

#     order = Order.objects.all()[0]
#     json, status_code = force_payment(order.order_id)
#     print(status_code)
#     print(json)
