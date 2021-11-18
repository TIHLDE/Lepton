from django.conf.urls import include, url
from rest_framework import routers

from app.career.views.job_post import JobPostViewSet
from app.career.views.weekly_business import WeeklyBusinessViewSet

router = routers.DefaultRouter()
router.register("weekly-business", WeeklyBusinessViewSet, basename="weekly-business")
router.register("jobpost", JobPostViewSet, basename="jobpost")

urlpatterns = [url(r"", include(router.urls))]
