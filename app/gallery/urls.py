from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from app.gallery.views import PictureViewSet

router = routers.DefaultRouter()
router.register("", PictureViewSet)

urlpatterns = [
    url(r"", include(router.urls)),
]
