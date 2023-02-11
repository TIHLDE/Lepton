from django.contrib import admin
from app.payment.models.order import Order

from app.payment.models.paid_event import PaidEvent

# Register your models here.
admin.site.register(PaidEvent)
admin.site.register(Order)
