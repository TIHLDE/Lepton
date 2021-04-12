from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from app.forms.views.form import FormViewSet

router = routers.DefaultRouter()
router.register("", FormViewSet)
router.register(
    r"(?P<form_id>[0-9a-f-]+)/submission", SubmissionViewSet
)

urlpatterns = [
    url(r"", include(router.urls)),
]