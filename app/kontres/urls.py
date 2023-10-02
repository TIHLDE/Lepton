from app.kontres.views.create_reservation import create_reservation
from django.urls import path

urlpatterns = [
    path('v1/create_reservation/', create_reservation, name='create_reservation'),
]
