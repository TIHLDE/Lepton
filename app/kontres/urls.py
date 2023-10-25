from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.kontres.views.bookable_item import BookableItemViewSet
from app.kontres.views.reservation import ReservationViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"reservations", ReservationViewSet, basename="reservation")
router.register(r"bookable_items", BookableItemViewSet, basename="bookable_item")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
]
