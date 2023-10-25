from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.kontres.views.bookable_item import BookableItemViewSet
from app.kontres.views.reservation import ReservationViewSet

router = DefaultRouter()
router.register(r"reservations", ReservationViewSet, basename="reservation")
router.register(r"bookable_items", BookableItemViewSet, basename="bookable_item")

urlpatterns = [
    path("", include(router.urls)),
]
