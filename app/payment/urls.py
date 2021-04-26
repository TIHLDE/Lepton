from django.conf.urls import include, url
from rest_framework import routers

from app.payment.views import RefundFormViewSet

router = routers.DefaultRouter()
router.register("refund-form", RefundFormViewSet, basename="refund-form")

# Register group viewpoints here
urlpatterns = [url(r"", include(router.urls))]
