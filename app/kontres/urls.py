from django.urls import path
from app.kontres.views.reservation import reservation_view

urlpatterns = [
    path('reservations/', reservation_view, name='reservations'),
    path('reservations/<int:reservation_id>/', reservation_view, name='single_reservation'),
]
