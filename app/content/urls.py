from rest_framework import routers

from .views import ItemViewSet, NewsViewSet, EventViewSet

router = routers.DefaultRouter()

# Register content viewpoints here

router.register('items', ItemViewSet)
router.register('news', NewsViewSet)
router.register('event', EventViewSet)


urlpatterns = router.urls
