from django.conf.urls import include, url
from rest_framework import routers

from app.career.views import WeeklyBusinessViewSet

router = routers.DefaultRouter()
router.register("weekly-business", WeeklyBusinessViewSet, basename="weekly-business")

urlpatterns = [url(r"", include(router.urls))]
