from django.urls import include, path, re_path
from rest_framework import routers

from app.payment.views.order import OrderViewSet
from app.payment.views.vipps_callback import vipps_callback

router = routers.DefaultRouter()

router.register("payment", OrderViewSet, basename="payment")

urlpatterns = [
    re_path(r"", include(router.urls)),
    path("v2/payment/<str:order_id>", vipps_callback),
]
