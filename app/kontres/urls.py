from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.kontres.views.reservation_new import ReservationViewSet
from app.kontres.views.fetch_bookable_items_new import BookableItemViewSet  # You'll need to create this class

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'bookable_items', BookableItemViewSet, basename='bookable_item')  # You'll need to create this class

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
