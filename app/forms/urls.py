from django.conf.urls import url
from rest_framework import routers
from django.urls import include

from app.forms.views.form import FormViewSet
#from app.forms.views.submission import SubmissionViewSet

router = routers.DefaultRouter()


router.register("", FormViewSet)
#router.register(
#    r"/(?P<form_id>[0-9a-f-]+)/submissions", SubmissionViewSet
#)

urlpatterns = [
    url(r"", include(router.urls)),
]
