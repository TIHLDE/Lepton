from django.contrib import admin

from .models.reservation import Reservation
from .models.bookable_item import BookableItem

admin.site.register(Reservation)
admin.site.register(BookableItem)

