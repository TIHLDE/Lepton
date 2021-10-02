from app.gallery.models import picture
from app.gallery.views import PictureViewSet
from django.conf.urls import url
from django.urls import include
from rest_framework import routers

router = routers.DefaultRouter()
router.register("", PictureViewSet)

urlpatterns = [
    url(r"", include(router.urls)),
]
