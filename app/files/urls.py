from rest_framework import routers

from app.content.views import (
    upload,
)

router = routers.DefaultRouter()

router.register("upload", upload)
