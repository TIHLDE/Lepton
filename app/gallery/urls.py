from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from app.gallery.views.album import AlbumViewSet
from app.gallery.views.picture import PictureViewSet

router = routers.DefaultRouter()
router.register("", AlbumViewSet)
router.register(r"(?P<slug>[^.]+)/pictures", PictureViewSet, basename="pictures")

urlpatterns = [
    url(r"", include(router.urls)),
]
