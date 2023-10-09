from django.contrib import admin
from .models.reservation import Reservation
from .models.bookable_item import BookableItem


class ReservationAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


class BookableItemAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


admin.site.register(Reservation, ReservationAdmin)
admin.site.register(BookableItem, BookableItemAdmin)
