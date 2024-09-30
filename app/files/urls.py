from django.urls import path
from rest_framework import routers

from app.files.views.file import FileView
from app.files.views.gallery import GalleryView
from app.files.views.upload import delete, upload

router = routers.DefaultRouter()

router.register("file", FileView)
router.register("gallery", GalleryView)

urlpatterns = [
    path("upload/", upload),
    path("delete-file/<str:container_name>/<str:blob_name>/", delete),
]
