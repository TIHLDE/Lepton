from django.contrib import admin

from app.kontresv2.models.bookable_item import BookableItem
from app.kontresv2.models.reservation import Reservation


class ReservationAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


class BookableItemAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


admin.site.register(Reservation, ReservationAdmin)
admin.site.register(BookableItem, BookableItemAdmin)
