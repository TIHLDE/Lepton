from django.conf.urls import include, url
from rest_framework import routers

from app.group.views import GroupViewSet, MembershipViewSet
from app.group.views.fine import FineViewSet
from app.group.views.law import LawViewSet
from app.group.views.group_form import GroupFormViewSet

router = routers.DefaultRouter()
router.register("groups", GroupViewSet, basename="group")
router.register(
    r"groups/(?P<slug>[^\.]+)/memberships", MembershipViewSet, basename="membership"
)
router.register(
    r"groups/(?P<slug>[^\.]+)/forms", GroupFormViewSet, basename="group_forms",
)
router.register(r"group/(?P<slug>[^\.]+)/laws", LawViewSet, basename="law")
router.register(r"group/(?P<slug>[^\.]+)/fines", FineViewSet, basename="fine")


# Register group viewpoints here
urlpatterns = [url(r"", include(router.urls))]
