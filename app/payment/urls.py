from django.urls import include, re_path
from rest_framework import routers

from app.payment.views import RefundFormViewSet

router = routers.DefaultRouter()
router.register("refund-form", RefundFormViewSet, basename="refund-form")

# Register group viewpoints here
urlpatterns = [re_path(r"", include(router.urls))]
