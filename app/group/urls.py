from django.conf.urls import include, url
from rest_framework import routers

from app.group.views import GroupViewSet, MembershipViewSet
from app.group.views.fine import FineViewSet
from app.group.views.law import LawViewSet

router = routers.DefaultRouter()
router.register("group", GroupViewSet, basename="group")
router.register(
    r"group/(?P<slug>[^\.]+)/membership", MembershipViewSet, basename="membership"
)
router.register(r"group/(?P<slug>[^\.]+)/law", LawViewSet, basename="law")
router.register(r"group/(?P<slug>[^\.]+)/fines", FineViewSet, basename="fine")


# Register group viewpoints here
urlpatterns = [url(r"", include(router.urls))]
