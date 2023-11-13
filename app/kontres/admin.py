from django.contrib import admin

from app.kontres.models.bookable_item import BookableItem
from app.kontres.models.reservation import Reservation


class ReservationAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


class BookableItemAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


admin.site.register(Reservation, ReservationAdmin)
admin.site.register(BookableItem, BookableItemAdmin)
