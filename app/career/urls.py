from django.urls import include, re_path
from rest_framework import routers

from app.career.views.job_post import JobPostViewSet
from app.career.views.weekly_business import WeeklyBusinessViewSet

router = routers.DefaultRouter()
router.register("weekly-businesses", WeeklyBusinessViewSet, basename="weekly-business")
router.register("jobposts", JobPostViewSet, basename="jobpost")

urlpatterns = [re_path(r"", include(router.urls))]
