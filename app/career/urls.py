from django.conf.urls import include, url
from rest_framework import routers

from app.career.views import WeeklyBusinessViewSet

router = routers.DefaultRouter()
router.register("weekly_business", WeeklyBusinessViewSet, basename="weekly_business")

# Register carrer viewpoints here
urlpatterns = [url(r"", include(router.urls))]
