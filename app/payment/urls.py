from django.urls import include, path, re_path
from rest_framework import routers

from app.payment.views.order import OrderViewSet
from app.payment.views.vipps import VippsViewSet
from app.payment.views.vipps_util import check_vipps_payment

router = routers.DefaultRouter()

router.register("payments", OrderViewSet, basename="payment")
router.register(
    r"v2/payments/(?P<order_id>[0-9a-f-]+)", VippsViewSet, basename="payment"
)

urlpatterns = [
    re_path(r"", include(router.urls)),
    path("check-payment/", check_vipps_payment),
]
