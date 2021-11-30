from django.conf.urls import include, url
from rest_framework import routers

from app.group.views import GroupViewSet, MembershipViewSet
from app.group.views.group_form import GroupFormViewSet

router = routers.DefaultRouter()
router.register("groups", GroupViewSet, basename="group")
router.register(
    r"groups/(?P<slug>[^\.]+)/memberships", MembershipViewSet, basename="membership"
)
router.register(
    r"groups/(?P<slug>[^\.]+)/forms", GroupFormViewSet, basename="group_forms",
)

# Register group viewpoints here
urlpatterns = [url(r"", include(router.urls))]
