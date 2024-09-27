from django.urls import include, re_path
from rest_framework import routers

from app.index.views.feedback import FeedbackViewSet

router = routers.DefaultRouter()
router.register("feedbacks", FeedbackViewSet)
urlpatterns = [re_path(r"", include(router.urls))]
