from django.conf.urls import include, url
from rest_framework import routers

from app.group.views import GroupViewSet, MembershipViewSet

router = routers.DefaultRouter()
router.register("group", GroupViewSet, basename="group")
router.register(
    r"group/(?P<slug>[^\.]+)/membership", MembershipViewSet, basename="membership"
)

# Register group viewpoints here
urlpatterns = [url(r"", include(router.urls))]
