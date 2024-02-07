from django.contrib import admin

from app.payment.models.order import Order
from app.payment.models.paid_event import PaidEvent

# Register your models here.
admin.site.register(PaidEvent)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = ("user__first_name", "user__last_name", "user__user_id", "order_id")

    list_filter = ("event",)
