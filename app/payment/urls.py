from django.urls import include, re_path
from rest_framework import routers
from app.payment.views.order import OrderViewSet
from app.payment.views.vipps_callback import vipps_callback
# from app.payment.views import (

# )

router = routers.DefaultRouter()

router.register("payment", OrderViewSet, basename="payment")
# router.register("payment-callback", vipps_callback, basename="payment-callback")

urlpatterns = [
    re_path(r"", include(router.urls)),
]