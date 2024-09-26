from rest_framework import routers
from app.index.views.feedback import FeedbackViewSet
from django.urls import include, re_path


router = routers.DefaultRouter()
router.register("feedbacks", FeedbackViewSet)
urlpatterns = [
    re_path(r"", include(router.urls))
]