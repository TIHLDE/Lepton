from app.kontres.views.create_reservation import create_reservation
from app.kontres.views.fetch_all_reservations import fetch_all_reservations
from app.kontres.views.edit_reservation import edit_reservation
from app.kontres.views.fetch_reservation import fetch_reservation
from django.urls import path

urlpatterns = [
    path('create_reservation/', create_reservation, name='create_reservation'),
    path('fetch_all_reservations/', fetch_all_reservations, name='fetch_all_reservations'),
    path('edit_reservation/<int:reservation_id>/', edit_reservation, name='edit_reservation'),
    path('fetch_reservation/<int:reservation_id>/', fetch_reservation, name='fetch_reservation')
]
