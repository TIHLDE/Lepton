from django.urls import path
from app.kontres.views.reservation import reservation_view
from app.kontres.views.fetch_bookable_items import bookable_item_view

urlpatterns = [
    path('reservations/', reservation_view, name='reservations'),
    path('reservations/<uuid:reservation_id>/', reservation_view, name='single_reservation'),
    path('bookable_items/', bookable_item_view, name='bookable_items')
]
